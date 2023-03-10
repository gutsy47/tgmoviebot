import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ChatActions

import botkeyboards as bk
from dbspread import Service
from movieparser import FilmRu


# Init the bot
token = os.environ['BOT_KEY']
bot = Bot(token=token)
storage = MemoryStorage()  # Memory for FSM
dp = Dispatcher(bot, storage=storage)

# Init the GSpread Database service account
service = Service()

# Template keywords
keywords = ["name", "year", "time"]


# Template updater form
class TemplateForm(StatesGroup):
    template = State()


# Find movie form
class MovieForm(StatesGroup):
    request = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Welcome message when the bot starts"""
    await message.reply(
        "<b>Hello, world!</b>\n"
        "Я тут за главного в свопе. Команды две:\n"
        "🖌 Получить пост  - Из БД бот сформирует пост (если есть данные)\n"
        "🔍 Найти фильм - Поиск фильма на film.ru\n"
        "⚙️ Шаблон поста - Посмотреть текущий шаблон поста",
        parse_mode="HTML",
        reply_markup=bk.rk_main
    )


@dp.message_handler(commands=['menu'])
async def send_menu_keyboard(message: types.Message):
    """Just re-open the bk.rk_main keyboard"""
    await message.answer(
        "Меню открыто",
        reply_markup=bk.rk_main
    )


@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel any action"""
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    await message.reply("Действие отменено", reply_markup=bk.rk_main)


# ADD MOVIE START
@dp.message_handler(commands=["find_movie"])
@dp.message_handler(Text(equals="🔍 Найти фильм"))
async def find_movie(message: types.Message):
    await message.answer(
        text="Введите название фильма",
        reply_markup=bk.rk_cancel
    )
    await MovieForm.request.set()


@dp.message_handler(state=MovieForm.request)
async def process_find_movie(message: types.Message, state: FSMContext):
    await message.answer_chat_action(ChatActions.TYPING)
    movie: FilmRu = FilmRu(message.text)

    if not movie.name:
        await message.reply(
            "Фильм не найден",
            reply_markup=bk.rk_main
        )
        await state.finish()
    else:
        await message.reply_photo(
            photo=movie.poster,
            caption=f"<a href=\"{movie.link}\">{movie.name}</a>\nТы ищешь этот фильм?",
            reply_markup=bk.ik_is_right_movie,
            parse_mode="HTML"
        )
        await state.update_data(movie=movie)


@dp.callback_query_handler(lambda c: c.data == "rightMovie", state=MovieForm.request)
async def movie_found(callback_query: types.CallbackQuery, state: FSMContext):
    movie: FilmRu = (await state.get_data())["movie"]
    service.add_movie(movie)

    await bot.answer_callback_query(callback_query.id)

    await bot.edit_message_caption(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        caption=f"<a href=\"{movie.link}\">{movie.name}</a>\n"
                f"Нажми кнопку чтобы получить пост по этому фильму",
        parse_mode="HTML"
    )
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=bk.ik_found_to_post
    )
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "wrongMovie", state=MovieForm.request)
async def movie_not_found(callback_query: types.CallbackQuery, state: FSMContext):
    movie: FilmRu = (await state.get_data())["movie"]
    movie.set_next_movie()

    await bot.answer_callback_query(callback_query.id)

    if not movie.name:
        await bot.delete_message(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
        )
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Результаты закончились, фильм не найден",
            reply_markup=bk.rk_main
        )
        await state.finish()
    else:
        await bot.edit_message_media(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            media=types.input_media.InputMediaPhoto(movie.poster)
        )
        await bot.edit_message_caption(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            caption=f"<a href=\"{movie.link}\">{movie.name}</a>\nТы ищешь этот фильм?",
            parse_mode="HTML"
        )
        await bot.edit_message_reply_markup(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=bk.ik_is_right_movie
        )
        await state.update_data(movie=movie)


@dp.callback_query_handler(lambda c: c.data == "foundToPost")
async def found_to_post(callback_query: types.CallbackQuery):
    post = service.get_last_post()
    service.set_last_movie_status_true()
    await callback_query.answer()
    await bot.delete_message(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id
    )
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=post,
        parse_mode="HTML",
        reply_markup=bk.ik_found_is_posted
    )


# ADD MOVIE END


# GET POST START
@dp.message_handler(commands=['get_post'])
@dp.message_handler(Text(equals="🖌 Получить пост"))
async def get_post(message: types.Message):
    await message.answer_chat_action(ChatActions.TYPING)
    amount = service.get_post_amount(is_posted=False)
    post = service.get_post_message(index=0)
    await message.reply(
        f"<b>Не выложенных постов:</b> {amount}",
        parse_mode="HTML",
    )
    if amount > 0:
        await message.answer(
            post,
            parse_mode="HTML",
            reply_markup=bk.get_ik_post(index=0)
        )


@dp.callback_query_handler(lambda c: "newPost" in c.data)
async def change_post(callback_query: types.CallbackQuery):
    index = int(callback_query.data[7:])
    post = service.get_post_message(index=index)
    next_post = service.get_post_message(index=index+1)

    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=post,
        parse_mode="HTML"
    )
    is_last = True if not next_post else False
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=bk.get_ik_post(index, is_last=is_last)
    )


@dp.callback_query_handler(lambda c: "posted" in c.data)
async def post_sent(callback_query: types.CallbackQuery):
    index = int(callback_query.data[6:])
    service.set_movie_status_true(movie_index=index)
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=bk.get_ik_post(index, True)
    )


@dp.callback_query_handler(lambda c: c.data == "Pass")
async def pass_callback_query(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)


# GET POST END


# TEMPLATE SETTINGS START
@dp.message_handler(commands=['template'])
@dp.message_handler(Text(equals="⚙️ Шаблон поста"))
async def send_template(message: types.Message):
    await message.answer_chat_action(ChatActions.TYPING)
    template = service.get_post_template()
    await message.reply(
        template,
        parse_mode="HTML",
        reply_markup=bk.ik_template
    )


@dp.callback_query_handler(lambda c: c.data == "updTemplate")
async def update_template(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        "Напиши новый шаблон\n"
        "Ключевые слова (вместо них бот подставляет информацию):\n"
        "name - Название фильма\n"
        "year - Год выпуска\n"
        "time - Продолжительность\n"
        "score - Рейтинг\n"
        "genres - Жанр(ы)\n"
        "description - Описание\n",
        reply_markup=bk.rk_cancel
    )
    await TemplateForm.template.set()
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(lambda message: any(key not in message.text for key in keywords), state=TemplateForm.template)
async def process_template_invalid(message: types.Message):
    return await message.reply("Какого-то из ключевых слов нет в шаблоне.\nНапиши новый шаблон")


@dp.message_handler(lambda message: all(key in message.text for key in keywords), state=TemplateForm.template)
async def process_template(message: types.Message, state: FSMContext):
    await message.answer_chat_action(ChatActions.TYPING)
    await state.finish()
    service.update_post_template(message.html_text)
    await message.reply(
        f"<b>Шаблон обновлён:</b>\n{message.html_text}",
        parse_mode="HTML",
        reply_markup=bk.rk_main
    )


# TEMPLATE SETTINGS END


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

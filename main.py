import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ChatActions

import botkeyboards as bk
from dbspread import Service


# Init the bot
token = os.environ['BOT_KEY']
bot = Bot(token=token)
storage = MemoryStorage()  # Memory for FSM
dp = Dispatcher(bot, storage=storage)

# Init the GSpread Database service account
service = Service()

# Template keywords
keywords = ["name", "year", "time", "score", "genres", "description"]


# Template updater form
class TemplateForm(StatesGroup):
    template = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Welcome message when the bot starts"""
    await message.reply(
        "<b>Hello, world!</b>\n"
        "Я тут за главного в свопе. Пока ничего нет, жди обновлений\n"
        "<i>In progress:</i> Настройка шаблона",
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


# GET POST START
@dp.message_handler(commands=['get_post'])
@dp.message_handler(Text(equals="🖌 Получить пост(ы)"))
async def get_not_posted_amount(message: types.Message):
    await message.answer_chat_action(ChatActions.TYPING)
    amount = service.get_post_amount(is_posted=False)
    await message.reply(
        f"<b>Не выложенных постов:</b> {amount}\n"
        "Сколько постов мне отправить?",
        parse_mode="HTML",
        reply_markup=bk.ik_posts_amount
    )


@dp.callback_query_handler(lambda c: c.data in ["1Post", "2Post", "3Post"])
async def send_posts(callback_query: types.CallbackQuery):
    amount = int(callback_query.data[0])
    posts = service.get_post_message(amount)
    for post in posts:
        await bot.send_message(
            callback_query.from_user.id,
            post,
            parse_mode="HTML",
        )
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "Нажми кнопку, соответствующую номеру поста, если выложишь его",
        reply_markup=bk.get_ik_is_posted(amount)
    )


@dp.callback_query_handler(lambda c: c.data in ["1posted", "2posted", "3posted"])
async def post_sent(callback_query: types.CallbackQuery):
    movie_index = int(callback_query.data[0])
    movie_name = service.update_movie_status(movie_index=movie_index, is_posted=True)
    await bot.send_message(
        callback_query.from_user.id,
        f"Фильм <b>{movie_name}</b> был помечен как <i>выложенный</i>",
        parse_mode="HTML"
    )
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

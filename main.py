import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

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


@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel any action"""
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    await message.reply("Действие отменено", reply_markup=bk.rk_main)


# SETTINGS START
@dp.message_handler(commands=['settings'])
async def send_settings(message: types.Message):
    """Bot settings. The only command that requires interaction"""
    await message.reply(
        "⚙ <b>Настройки:</b>\n"
        "<b>Шаблон</b> - Настройки шаблона поста\n"
        "<b>Время</b> - Настройка времени отправки поста(ов)\n"
        "<b>Количество</b> - Настройка количества отправляемых постов",
        parse_mode="HTML",
        reply_markup=bk.ik_settings,
    )


# SETTINGS-TEMPLATE START
@dp.callback_query_handler(lambda c: c.data == "template")
async def send_template(callback_query: types.CallbackQuery):
    template = service.get_post_template()
    await bot.send_message(
        callback_query.from_user.id,
        template,
        parse_mode="HTML",
        reply_markup=bk.ik_template
    )
    await bot.answer_callback_query(callback_query.id)


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
    await state.finish()
    service.update_post_template(message.html_text)
    await message.reply(
        f"<b>Шаблон обновлён:</b>\n{message.html_text}",
        parse_mode="HTML",
        reply_markup=bk.rk_main
    )


# SETTINGS-TEMPLATE END


@dp.callback_query_handler(lambda c: c.data == "time")
async def send_time(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Soon")
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data == "amount")
async def send_amount(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Soon")
    await bot.answer_callback_query(callback_query.id)


# SETTINGS END


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

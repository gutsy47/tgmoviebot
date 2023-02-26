from aiogram.types import inline_keyboard as ik, reply_keyboard as rk

rk_main = rk.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
rk_main.add(
    rk.KeyboardButton("/settings")
)

rk_cancel = rk.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
rk_cancel.add(
    rk.KeyboardButton("Отмена")
)

ik_settings = ik.InlineKeyboardMarkup(row_width=3)
ik_settings.add(
    ik.InlineKeyboardButton("Шаблон", callback_data="template"),
    ik.InlineKeyboardButton("Время", callback_data="time"),
    ik.InlineKeyboardButton("Количество", callback_data="amount")
)

ik_template = ik.InlineKeyboardMarkup(row_width=1)
ik_template.add(
    ik.InlineKeyboardButton("Изменить", callback_data="updTemplate")
)

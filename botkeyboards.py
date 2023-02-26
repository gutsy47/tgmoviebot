from aiogram.types import inline_keyboard as ik, reply_keyboard as rk

rk_main = rk.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
rk_main.add(
    rk.KeyboardButton("⚙️ Шаблон поста")
)

rk_cancel = rk.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
rk_cancel.add(
    rk.KeyboardButton("Отмена")
)

ik_template = ik.InlineKeyboardMarkup(row_width=1)
ik_template.add(
    ik.InlineKeyboardButton("Изменить", callback_data="updTemplate")
)

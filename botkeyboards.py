from aiogram.types import inline_keyboard as ik, reply_keyboard as rk

rk_main = rk.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
rk_main.add(
    rk.KeyboardButton("⚙️ Шаблон поста"),
    rk.KeyboardButton("🖌 Получить пост(ы)")
)

rk_cancel = rk.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
rk_cancel.add(
    rk.KeyboardButton("Отмена")
)

ik_template = ik.InlineKeyboardMarkup(row_width=1)
ik_template.add(
    ik.InlineKeyboardButton("Изменить", callback_data="updTemplate")
)

ik_posts_amount = ik.InlineKeyboardMarkup(row_width=3)
ik_posts_amount.add(
    ik.InlineKeyboardButton('1', callback_data="1Post"),
    ik.InlineKeyboardButton('2', callback_data="2Post"),
    ik.InlineKeyboardButton('3', callback_data="3Post"),
)


def get_ik_is_posted(amount: int = 1):
    keyboard = ik.InlineKeyboardMarkup(row_width=3)
    for i in range(1, amount+1):
        keyboard.insert(ik.InlineKeyboardButton(f"✅ {i}", callback_data=f"{i}posted"))
    return keyboard

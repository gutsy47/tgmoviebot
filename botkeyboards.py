from aiogram.types import inline_keyboard as ik, reply_keyboard as rk

rk_main = rk.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
rk_main.add(
    rk.KeyboardButton("🖌 Получить пост"),
    rk.KeyboardButton("🔍 Найти фильм"),
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


def get_ik_post(index: int = 0, is_posted: bool = False):
    ik_post = ik.InlineKeyboardMarkup(row_width=2)
    if index > 0:
        ik_post.add(ik.InlineKeyboardButton('◀️', callback_data=f"newPost{index-1}"))
    ik_post.insert(ik.InlineKeyboardButton('▶️', callback_data=f"newPost{index+1}"))
    if is_posted:
        ik_post.add(ik.InlineKeyboardButton("✅ Выложен", callback_data="Pass"))
    else:
        ik_post.add(ik.InlineKeyboardButton('📌 Выложить', callback_data=f"posted{index}"))
    return ik_post


ik_is_right_movie = ik.InlineKeyboardMarkup(row_width=2)
ik_is_right_movie.add(
    ik.InlineKeyboardButton("✅ Да", callback_data="rightMovie"),
    ik.InlineKeyboardButton("❌ Нет", callback_data="wrongMovie")
)

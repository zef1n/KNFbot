from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
cities = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Екатеринбург', callback_data="ekb")],
        [InlineKeyboardButton(text='Челябинск', callback_data="chlb")],
        [InlineKeyboardButton(text='Магнитогорск', callback_data="mgn")]      ,
        [InlineKeyboardButton(text='Тюмень', callback_data="tmn")]

    ]
)
ekb_areas = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Академический', callback_data="akadem_ekb")],
        [InlineKeyboardButton(text='Верх-Иссетский', callback_data="vis_ekb")],
        [InlineKeyboardButton(text='Железнодорожный', callback_data="zhd_ekb")],
        [InlineKeyboardButton(text='Кировский', callback_data="kir_ekb")],
        [InlineKeyboardButton(text='Ленинский', callback_data="len_ekb")],
        [InlineKeyboardButton(text='Октябрьский', callback_data="oct_ekb")],
        [InlineKeyboardButton(text='Орджоникидзевский', callback_data="oed_ekb")],
        [InlineKeyboardButton(text='Чкаловский', callback_data="chk_ekb")],
        [InlineKeyboardButton(text='назад', callback_data="back")]
    ]
)
Back_button= InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data="Back")]
    ]
)
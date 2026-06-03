from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Навбат гирифтан")],
            [KeyboardButton(text="🎫 Навбати ман"), KeyboardButton(text="📅 Вақт гирифтан")],
            [KeyboardButton(text="⚙️ Танзимот")],
        ],
        resize_keyboard=True
    )


def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Рақами телефонам", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def orgs_keyboard(orgs: list):
    buttons = [[InlineKeyboardButton(text=org['name'], callback_data=f"org_{org['id']}")] for org in orgs]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def branches_keyboard(branches: list):
    buttons = [[InlineKeyboardButton(text=b['name'], callback_data=f"branch_{b['id']}")] for b in branches]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def queues_keyboard(queues: list):
    buttons = [
        [InlineKeyboardButton(
            text=f"{q['name']} — ⏳ {q['waiting_count']} нафар",
            callback_data=f"queue_{q['id']}"
        )]
        for q in queues
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_ticket_keyboard(ticket_number: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Навбатро рад кардан",
                callback_data=f"cancel_ticket_{ticket_number}"  # Ном бояд маҳз ҳамин хел бошад!
            )
        ]
    ])


def rating_keyboard(ticket_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 1", callback_data=f"rate_{ticket_id}_1"),
            InlineKeyboardButton(text="⭐ 2", callback_data=f"rate_{ticket_id}_2"),
            InlineKeyboardButton(text="⭐ 3", callback_data=f"rate_{ticket_id}_3"),
            InlineKeyboardButton(text="⭐ 4", callback_data=f"rate_{ticket_id}_4"),
            InlineKeyboardButton(text="⭐ 5", callback_data=f"rate_{ticket_id}_5"),
        ]
    ])
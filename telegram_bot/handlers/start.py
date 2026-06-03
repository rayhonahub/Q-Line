from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from ..states import RegisterStates, QueueStates
from ..keyboards import main_menu, phone_keyboard
from ..api_client import get_or_create_user, get_my_tickets

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    # Check if user is registered by looking up their telegram_id
    from ..api_client import get_or_create_user as _check
    # We use get_my_tickets as a registration probe —
    # 200 with [] means registered but no active tickets
    # 401/404 means not registered
    from ..api_client import check_user_registered
    is_registered = await check_user_registered(message.from_user.id)

    if is_registered:
        tickets = await get_my_tickets(message.from_user.id)
        if tickets:
            ticket = tickets[0]
            status_map = {
                "waiting": "⏳ Интизор",
                "called":  "📢 Даъват шудед!",
                "serving": "✅ Хизматрасонӣ",
            }
            status_label = status_map.get(ticket.get("status", ""), ticket.get("status", ""))
            await message.answer(
                f"👋 Хуш омадед, *{message.from_user.first_name}!*\n\n"
                f"🎫 Навбати фаъол: *{ticket.get('number')}*\n"
                f"📋 {ticket.get('organization')} — {ticket.get('branch')}\n"
                f"📊 Ҳолат: {status_label}\n"
                f"👥 Пеш аз шумо: {ticket.get('position', 0)} нафар",
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
        else:
            await message.answer(
                f"👋 Хуш омадед, *{message.from_user.first_name}!*\n\n"
                f"Чӣ хизмат?",
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
    else:
        await message.answer(
            f"👋 Салом, *{message.from_user.first_name}!*\n\n"
            f"Ба Q-Line хуш омадед!\n"
            f"Барои давом кардан рақами телефонатонро диҳед 👇",
            parse_mode="Markdown",
            reply_markup=phone_keyboard()
        )
        await state.set_state(RegisterStates.waiting_phone)


@router.message(RegisterStates.waiting_phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone

    result = await get_or_create_user(
        telegram_id=message.from_user.id,
        phone=phone,
        username=message.from_user.username,
    )

    await state.clear()

    if result.get('success') or result.get('id'):
        await message.answer(
            f"✅ *Муваффақ қайд шудед!*\n\n"
            f"Ҳозир навбат гирифта метавонед 👇",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            "❌ Хато рӯй дод. Дубора /start занед.",
            reply_markup=main_menu()
        )


# ── Main menu button handlers ──────────────────────────────────────────────────

@router.message(F.text == "📋 Навбат гирифтан")
async def menu_join_queue(message: Message, state: FSMContext):
    """User tapped 'Join Queue' from main menu — start the org selection flow."""
    await state.clear()
    from ..api_client import get_organizations
    orgs = await get_organizations()
    if not orgs:
        await message.answer("⚠️ Ҳеҷ ташкилоте ёфт нашуд.")
        return
    from ..keyboards import orgs_keyboard
    await message.answer("🏢 Ташкилотро интихоб кунед:", reply_markup=orgs_keyboard(orgs))
    await state.set_state(QueueStates.select_org)


@router.message(F.text == "🎫 Навбати ман")
async def menu_my_ticket(message: Message, state: FSMContext):
    """User tapped 'My Queue' — show their active tickets."""
    tickets = await get_my_tickets(message.from_user.id)
    if not tickets:
        await message.answer(
            "📭 Шумо ҳоло дар ҳеҷ навбате нестед.\n"
            "Барои навбат гирифтан «📋 Навбат гирифтан»-ро пахш кунед.",
            reply_markup=main_menu()
        )
        return

    ticket = tickets[0]
    status_map = {
        "waiting": "⏳ Интизор",
        "called":  "📢 Даъват шудед!",
        "serving": "✅ Хизматрасонӣ",
    }
    status_label = status_map.get(ticket.get("status", ""), ticket.get("status", ""))
    window_text = f"\n🪟 Тиреза: {ticket['window']}" if ticket.get("window") else ""

    from ..keyboards import cancel_ticket_keyboard
    await message.answer(
        f"🎫 Рақам: *{ticket.get('number')}*\n"
        f"📋 {ticket.get('organization')} — {ticket.get('branch')}\n"
        f"📊 Ҳолат: {status_label}\n"
        f"👥 Пеш аз шумо: {ticket.get('position', 0)} нафар"
        f"{window_text}",
        parse_mode="Markdown",
        reply_markup=cancel_ticket_keyboard(ticket.get('id'))
    )


@router.message(F.text == "📅 Вақт гирифтан")
async def menu_appointment(message: Message, state: FSMContext):
    await message.answer("🚧 Ин функсия ҳоло дар коркард аст.", reply_markup=main_menu())


@router.message(F.text == "⚙️ Танзимот")
async def menu_settings(message: Message, state: FSMContext):
    await message.answer(
        f"⚙️ *Танзимот*\n\n"
        f"👤 Telegram ID: `{message.from_user.id}`\n"
        f"👤 Username: @{message.from_user.username or '—'}",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
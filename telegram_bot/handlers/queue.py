import httpx
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..states import QueueStates
from ..keyboards import (
    orgs_keyboard,
    branches_keyboard,
    queues_keyboard,
    cancel_ticket_keyboard,
    main_menu,
)
from ..api_client import get_organizations, get_branches, get_queues, get_my_ticket
from ..config import API_BASE_URL, BOT_SECRET

router = Router()

BACKEND_URL = API_BASE_URL
BOT_HEADERS = {"X-Bot-Secret": BOT_SECRET}


# ─── Choose organisation ───────────────────────────────────────────────────────
# NOTE: The entry point ("📋 Навбат гирифтан") is handled in start.py
# This file only handles the callback steps AFTER org selection begins.

@router.callback_query(QueueStates.select_org, F.data.startswith("org_"))
async def org_chosen(call: CallbackQuery, state: FSMContext):
    org_id = int(call.data.split("_")[1])
    await state.update_data(org_id=org_id)

    branches = await get_branches(org_id)
    if not branches:
        await call.message.edit_text("⚠️ Шӯъбае ёфт нашуд.")
        return
    await call.message.edit_text("🏬 Шӯъбаро интихоб кунед:", reply_markup=branches_keyboard(branches))
    await state.set_state(QueueStates.select_branch)


# ─── Choose branch ─────────────────────────────────────────────────────────────

@router.callback_query(QueueStates.select_branch, F.data.startswith("branch_"))
async def branch_chosen(call: CallbackQuery, state: FSMContext):
    branch_id = int(call.data.split("_")[1])
    await state.update_data(branch_id=branch_id)

    queues = await get_queues(branch_id)
    if not queues:
        await call.message.edit_text("⚠️ Навбате ёфт нашуд.")
        return
    await call.message.edit_text("📋 Навбатро интихоб кунед:", reply_markup=queues_keyboard(queues))
    await state.set_state(QueueStates.select_queue)


# ─── Choose queue → create ticket ─────────────────────────────────────────────

@router.callback_query(QueueStates.select_queue, F.data.startswith("queue_"))
async def queue_chosen(call: CallbackQuery, state: FSMContext):
    queue_id = int(call.data.split("_")[1])
    telegram_id = call.from_user.id

    await call.message.edit_text("⏳ Дар ҳоли коркард...")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{BACKEND_URL}/api/queues/telegram/join/",
                json={"telegram_id": telegram_id, "queue_id": queue_id},
                headers=BOT_HEADERS,
            )
    except httpx.RequestError as exc:
        await call.message.edit_text(f"❌ Хатои пайвастшавӣ: {exc}")
        return

    if resp.status_code == 201:
        data = resp.json()
        ticket_number = data["ticket_number"]
        position = data["position"]
        queue_name = data.get("queue", "")
        branch_name = data.get("branch", "")

        await state.update_data(ticket_number=ticket_number)
        await state.set_state(QueueStates.in_queue)

        # Edit the inline message to show ticket confirmation
        await call.message.edit_text(
            f"✅ <b>Навбат гирифта шуд!</b>\n\n"
            f"🏢 {branch_name} — {queue_name}\n"
            f"🎫 Рақами шумо: <b>{ticket_number}</b>\n"
            f"👥 Пеш аз шумо: <b>{position}</b> нафар\n\n"
            f"📌 Мунтазири даъват бошед.",
            reply_markup=cancel_ticket_keyboard(ticket_number),
            parse_mode="HTML",
        )
        # Send a new message to show the reply keyboard menu
        await call.message.answer(
            "Барои идома додан менюро истифода баред 👇",
            reply_markup=main_menu()
        )

    elif resp.status_code == 409:
        data = resp.json()
        await call.message.edit_text(
            f"⚠️ {data.get('detail', 'Шумо аллакай дар навбат ҳастед.')}\n"
            f"🎫 Рақами шумо: <b>{data.get('ticket_number', '—')}</b>",
            parse_mode="HTML",
        )
        await call.message.answer("Менюро истифода баред 👇", reply_markup=main_menu())

    elif resp.status_code == 401:
        await call.message.edit_text(
            "❌ Шумо дар система қайд нашудаед.\n"
            "Лутфан аввал /start занед ва қайд шавед."
        )

    else:
        try:
            detail = resp.json().get("detail", "Хатои номаълум")
        except Exception:
            detail = f"HTTP {resp.status_code}"
        await call.message.edit_text(f"❌ Хато: {detail}")


# ─── Cancel ticket ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("cancel_ticket_"))
async def cancel_ticket_handler(call: CallbackQuery, state: FSMContext):
    ticket_number = call.data.split("cancel_ticket_")[1]
    telegram_id = call.from_user.id

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            status_resp = await client.get(
                f"{BACKEND_URL}/api/queues/telegram/ticket/{ticket_number}/status/",
                params={"telegram_id": telegram_id},
                headers=BOT_HEADERS,
            )
            if status_resp.status_code != 200:
                await call.message.edit_text("❌ Чиптаро ёфтан мумкин набуд.")
                return

            ticket_id = status_resp.json().get("id")
            cancel_resp = await client.post(
                f"{BACKEND_URL}/api/queues/tickets/{ticket_id}/cancel/",
                headers=BOT_HEADERS,
            )
    except httpx.RequestError as exc:
        await call.message.edit_text(f"❌ Хатои пайвастшавӣ: {exc}")
        return

    if cancel_resp.status_code == 200:
        await call.message.edit_text("✅ Навбати шумо бекор карда шуд.")
        await state.clear()
        await call.message.answer("Менюро истифода баред 👇", reply_markup=main_menu())
    else:
        detail = cancel_resp.json().get("detail", "Хатои номаълум")
        await call.message.edit_text(f"❌ {detail}")


# ─── /mystatus command ─────────────────────────────────────────────────────────

@router.message(F.text == "/mystatus")
async def my_status_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_number = data.get("ticket_number")

    if not ticket_number:
        await message.answer(
            "❌ Шумо ҳоло дар ҳеҷ навбате нестед.",
            reply_markup=main_menu()
        )
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BACKEND_URL}/api/queues/telegram/ticket/{ticket_number}/status/",
                params={"telegram_id": message.from_user.id},
                headers=BOT_HEADERS,
            )
    except httpx.RequestError as exc:
        await message.answer(f"❌ Хатои пайвастшавӣ: {exc}")
        return

    if resp.status_code != 200:
        await message.answer("❌ Чиптаро ёфтан мумкин набуд.")
        return

    d = resp.json()
    status_map = {
        "waiting":   "⏳ Интизор",
        "called":    "📢 Даъват шудед!",
        "serving":   "✅ Хизматрасонӣ",
        "completed": "✔️ Тамом шуд",
        "cancelled": "❌ Бекор карда шуд",
        "no_show":   "⚠️ Наомадед",
    }
    status_label = status_map.get(d["status"], d["status"])
    position_text = f"\n👥 Пеш аз шумо: {d['position']} нафар" if d["status"] == "waiting" else ""
    window_text = f"\n🪟 Тиреза: {d['window']}" if d.get("window") else ""

    await message.answer(
        f"🎫 Рақам: <b>{d['number']}</b>\n"
        f"📊 Ҳолат: {status_label}"
        f"{position_text}{window_text}",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
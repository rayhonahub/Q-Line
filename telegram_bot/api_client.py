import httpx
from .config import API_BASE_URL, BOT_SECRET

BOT_HEADERS = {"X-Bot-Secret": BOT_SECRET}


def _safe_json(response: httpx.Response) -> dict | list:
    """Return parsed JSON or a safe fallback — never raises JSONDecodeError."""
    try:
        return response.json()
    except Exception:
        return {"detail": f"HTTP {response.status_code}", "status_code": response.status_code}


async def get_or_create_user(telegram_id: int, phone: str, username: str = None):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE_URL}/api/accounts/auth/telegram/",
            json={"telegram_id": telegram_id, "phone": phone, "username": username or str(telegram_id)},
            headers=BOT_HEADERS,
        )
        return _safe_json(resp)


async def get_organizations():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/api/orgs/public/")
        return _safe_json(resp) if resp.status_code == 200 else []


async def get_branches(org_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/api/orgs/{org_id}/branches/public/")
        return _safe_json(resp) if resp.status_code == 200 else []


async def get_queues(branch_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE_URL}/api/queues/branches/{branch_id}/queues/")
        return _safe_json(resp) if resp.status_code == 200 else []


async def create_ticket(queue_id: int, telegram_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE_URL}/api/queues/telegram/join/",
            json={"queue_id": queue_id, "telegram_id": telegram_id},
            headers=BOT_HEADERS,
        )
        return resp.status_code, _safe_json(resp)


async def get_my_ticket(telegram_id: int, ticket_number: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{API_BASE_URL}/api/queues/telegram/ticket/{ticket_number}/status/",
            params={"telegram_id": telegram_id},
            headers=BOT_HEADERS,
        )
        return _safe_json(resp) if resp.status_code == 200 else {}


async def get_my_tickets(telegram_id: int) -> list:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{API_BASE_URL}/api/queues/tickets/telegram/{telegram_id}/",
            headers=BOT_HEADERS,
        )
        if resp.status_code == 200:
            return _safe_json(resp)
        return []  # 404 or any error → empty list, no crash


async def cancel_ticket(ticket_id: int, telegram_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE_URL}/api/queues/tickets/{ticket_id}/cancel/",
            json={"telegram_id": telegram_id},
            headers=BOT_HEADERS,
        )
        return resp.status_code, _safe_json(resp)


async def rate_ticket(ticket_id: int, rating: int):
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{API_BASE_URL}/api/queues/tickets/{ticket_id}/rating/",
            json={"rating": rating},
            headers=BOT_HEADERS,
        )
        return resp.status_code, _safe_json(resp)


async def check_user_registered(telegram_id: int) -> bool:
    """
    Returns True if a User with this telegram_id exists in the backend.
    Uses the my-tickets endpoint — 200 (even empty list) = registered, anything else = not registered.
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{API_BASE_URL}/api/queues/tickets/telegram/{telegram_id}/",
                headers=BOT_HEADERS,
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False
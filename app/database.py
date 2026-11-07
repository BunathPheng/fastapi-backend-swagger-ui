import os
from typing import Any

import httpx


class DatabaseUnavailable(RuntimeError):
    pass


class SupabaseRepository:
    def __init__(self) -> None:
        self.url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.key = (
            os.getenv("SUPABASE_SECRET_KEY", "").strip()
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        )
        self.base_url = f"{self.url}/rest/v1" if self.url else ""

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.key)

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        table: str,
        *,
        params: dict[str, str] | None = None,
        json: Any = None,
        prefer: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self.configured:
            raise DatabaseUnavailable("Supabase is not configured.")
        headers = self._headers()
        if prefer:
            headers["Prefer"] = prefer
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.request(
                    method,
                    f"{self.base_url}/{table}",
                    headers=headers,
                    params=params,
                    json=json,
                )
        except httpx.HTTPError as error:
            raise DatabaseUnavailable("Unable to connect to Supabase.") from error
        if not response.is_success:
            raise DatabaseUnavailable(f"Supabase request failed with status {response.status_code}.")
        if not response.content:
            return []
        return response.json()

    async def list_rows(self, table: str, order: str = "sort_order.asc") -> list[dict[str, Any]]:
        return await self._request(
            "GET",
            table,
            params={"select": "*", "is_published": "eq.true", "order": order},
        )

    async def get_row(self, table: str, row_id: int) -> dict[str, Any] | None:
        rows = await self._request(
            "GET",
            table,
            params={
                "select": "*",
                "is_published": "eq.true",
                "id": f"eq.{row_id}",
                "limit": "1",
            },
        )
        return rows[0] if rows else None

    async def create_contact(self, payload: dict[str, Any]) -> dict[str, Any]:
        rows = await self._request(
            "POST",
            "contact_submissions",
            json=payload,
            prefer="return=representation",
        )
        if not rows:
            raise DatabaseUnavailable("Supabase did not return the saved contact submission.")
        return rows[0]


repository = SupabaseRepository()

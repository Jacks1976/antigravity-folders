"""
Organizations router - public organization listing for landing page.
Returns a small set of public fields for active organizations.
All endpoints return HTTP 200 with response envelope.
"""
from fastapi import APIRouter, Response
from db import get_db_connection

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.get("/public")
async def public_organizations(response: Response):
    """Return list of active organizations (public fields)."""
    try:
        with get_db_connection() as conn:
            conn.row_factory = None
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, slug, city, country, logo_url FROM organizations WHERE is_active = 1 ORDER BY name ASC")
            rows = cursor.fetchall()

            results = []
            for r in rows:
                # r may be sqlite3.Row but we select by index to be safe
                results.append({
                    "id": r[0],
                    "name": r[1],
                    "slug": r[2],
                    "city": r[3] or "",
                    "country": r[4] or "",
                    "logo_url": r[5] or None,
                })

        response.status_code = 200
        return {"ok": True, "data": {"results": results}, "error_key": None}
    except Exception:
        response.status_code = 200
        return {"ok": False, "data": None, "error_key": "internal_error"}

from fastapi import APIRouter, Query
import requests

router = APIRouter(prefix="/bible", tags=["bible"])


@router.get("/passage")
def get_passage(ref: str = Query(..., description="Passage reference, e.g. John 3:16"), translation: str = Query(None)):
    """Proxy a simple Bible API (bible-api.com) to fetch passage text.
    Falls back to bible-api.com which does not require a key for many translations.
    """
    try:
        # sanitize ref for URL
        ref_encoded = requests.utils.requote_uri(ref)
        url = f"https://bible-api.com/{ref_encoded}"
        if translation:
            url = f"{url}?translation={translation}"

        resp = requests.get(url, timeout=10)
        # Pass through the JSON body, wrapped in our envelope
        if resp.status_code == 200:
            return {"ok": True, "data": resp.json(), "error_key": None}
        else:
            return {"ok": False, "data": None, "error_key": "bible.fetch_failed", "detail": resp.text}
    except Exception as e:
        return {"ok": False, "data": None, "error_key": "internal_error", "detail": str(e)}

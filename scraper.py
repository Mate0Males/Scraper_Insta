import requests
from fake_useragent import UserAgent
import json
import time
import sys

SESSION_ID = "26435784078%3ADxV5d5QS8b3FdY%3A24%3AAYipi3MHTdyTSTTNPRClkE-2oDpRzBttJ7AL94wAtQ"

# ─────────────────────────────────────────────────────────────────────────────
# Session bootstrap
# ─────────────────────────────────────────────────────────────────────────────

_ua: str = ""


def _get_ua() -> str:
    global _ua
    if not _ua:
        _ua = UserAgent().random
    return _ua


def _bootstrap_session(session_id: str) -> requests.Session:
    """Creates a Session, sets the sessionid cookie, and fetches a CSRF token."""
    s = requests.Session()
    s.cookies.set("sessionid", session_id, domain=".instagram.com")
    try:
        s.get(
            "https://www.instagram.com/",
            headers={"user-agent": _get_ua(), "accept": "text/html"},
            timeout=10,
        )
    except Exception as e:
        print(f"[warn] No se pudo inicializar sesión: {e}")
    return s


def _headers(session: requests.Session, referer: str = "") -> dict:
    csrf = session.cookies.get("csrftoken", "")
    h = {
        "authority": "www.instagram.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": _get_ua(),
        "x-ig-app-id": "936619743392459",
        "x-requested-with": "XMLHttpRequest",
    }
    if csrf:
        h["x-csrftoken"] = csrf
    if referer:
        h["referer"] = referer
    return h


# ─────────────────────────────────────────────────────────────────────────────
# User details
# ─────────────────────────────────────────────────────────────────────────────

def get_user_details(username: str, session: requests.Session) -> dict | None:
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    try:
        resp = session.get(
            url,
            headers=_headers(session, f"https://www.instagram.com/{username}/"),
            timeout=10,
        )
        if resp.status_code == 200:
            u = resp.json().get("data", {}).get("user", {})
            return {
                "user_id": u.get("id"),
                "username": u.get("username"),
                "full_name": u.get("full_name", ""),
                "biography": u.get("biography", ""),
                "follower_count": u.get("edge_followed_by", {}).get("count", 0),
                "following_count": u.get("edge_follow", {}).get("count", 0),
                "post_count": u.get("edge_owner_to_timeline_media", {}).get("count", 0),
                "is_private": u.get("is_private", False),
                "is_verified": u.get("is_verified", False),
                "profile_pic_url": u.get("profile_pic_url_hd", ""),
                "external_url": u.get("external_url", ""),
            }
        print(f"[error] Perfil de {username}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"[error] Perfil de {username}: {e}")
    return None


# ─────────────────────────────────────────────────────────────────────────────
# User posts  (returns media_id too — needed for comments)
# ─────────────────────────────────────────────────────────────────────────────

def get_user_posts(
    username: str,
    session: requests.Session,
    limit: int = 10,
) -> list[dict]:
    """
    Returns list of dicts: {url, code, media_id}
    media_id is the numeric Instagram ID required for the comments endpoint.
    """
    user_info = get_user_details(username, session)
    if not user_info or not user_info.get("user_id"):
        print(f"[error] No se pudo obtener user_id de {username}")
        return []

    user_id = user_info["user_id"]
    posts: list[dict] = []
    end_cursor: str | None = None
    has_next = True

    while has_next and len(posts) < limit:
        params: dict = {"count": min(limit - len(posts), 12)}
        if end_cursor:
            params["max_id"] = end_cursor

        try:
            resp = session.get(
                f"https://www.instagram.com/api/v1/feed/user/{user_id}/",
                headers=_headers(session, f"https://www.instagram.com/{username}/"),
                params=params,
                timeout=10,
            )
            if resp.status_code != 200:
                print(f"[error] Feed de {username}: HTTP {resp.status_code}")
                break

            data = resp.json()
            for item in data.get("items", []):
                code = item.get("code")
                media_id = item.get("pk") or item.get("id")
                if code and media_id:
                    posts.append({
                        "url": f"https://www.instagram.com/p/{code}/",
                        "code": code,
                        "media_id": str(media_id),
                    })

            has_next = data.get("more_available", False)
            end_cursor = data.get("next_max_id")
            if has_next and len(posts) < limit:
                time.sleep(0.5)

        except Exception as e:
            print(f"[error] Feed de {username}: {e}")
            break

    return posts[:limit]


# ─────────────────────────────────────────────────────────────────────────────
# Comments  (uses the correct private-API endpoint)
# ─────────────────────────────────────────────────────────────────────────────

def get_post_comments(
    media_id: str,
    post_code: str,
    session: requests.Session,
    limit: int = 3,
) -> dict:
    """
    Fetches comments via /api/v1/media/{media_id}/comments/
    Returns {post_code, comments, total_comments, has_more_comments, error}.
    """
    result = {
        "post_code": post_code,
        "comments": [],
        "total_comments": 0,
        "has_more_comments": False,
        "error": None,
    }

    try:
        resp = session.get(
            f"https://www.instagram.com/api/v1/media/{media_id}/comments/",
            headers=_headers(session, f"https://www.instagram.com/p/{post_code}/"),
            params={"can_support_threading": "true", "permalink_enabled": "false"},
            timeout=10,
        )

        if resp.status_code == 200:
            data = resp.json()
            result["total_comments"] = data.get("comment_count", 0)
            result["has_more_comments"] = data.get("can_view_more_preview_comments", False)

            for c in data.get("comments", [])[:limit]:
                result["comments"].append({
                    "id": str(c.get("pk") or c.get("id", "")),
                    "username": c.get("user", {}).get("username"),
                    "user_id": str(c.get("user", {}).get("pk") or c.get("user", {}).get("id", "")),
                    "text": c.get("text", ""),
                    "created_at": c.get("created_at"),
                    "likes": c.get("comment_like_count", 0),
                    "reply_count": c.get("child_comment_count", 0),
                })
        elif resp.status_code == 401:
            result["error"] = "Sesión inválida o expirada (401) — renovar SESSION_ID"
        elif resp.status_code == 429:
            result["error"] = "Rate limit alcanzado (429) — esperar antes de continuar"
        elif resp.status_code == 404:
            result["error"] = "Post no encontrado o eliminado (404)"
        else:
            result["error"] = f"HTTP {resp.status_code}: {resp.text[:200]}"

    except Exception as e:
        result["error"] = f"Excepción: {e}"

    return result


# ─────────────────────────────────────────────────────────────────────────────
# High-level helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_posts_with_comments(
    username: str,
    session: requests.Session,
    post_limit: int = 10,
    comment_limit: int = 10,
) -> dict:
    result = {
        "success": False,
        "user_info": None,
        "posts": [],
        "total_posts_found": 0,
        "total_comments_collected": 0,
        "error": None,
    }

    user_info = get_user_details(username, session)
    if not user_info:
        result["error"] = f"No se pudo obtener información del usuario @{username}"
        return result
    result["user_info"] = user_info

    posts = get_user_posts(username, session, post_limit)
    if not posts:
        result["error"] = f"No se encontraron posts para @{username}"
        return result

    result["total_posts_found"] = len(posts)
    print(f"\n[info] Obteniendo comentarios de {len(posts)} posts de @{username}…")

    for i, post in enumerate(posts, 1):
        print(f"  [{i}/{len(posts)}] {post['url']}")
        cd = get_post_comments(post["media_id"], post["code"], session, comment_limit)

        result["posts"].append({
            "url": post["url"],
            "code": post["code"],
            "media_id": post["media_id"],
            "comments": cd["comments"],
            "total_comments": cd["total_comments"],
            "has_more_comments": cd["has_more_comments"],
            "error": cd.get("error"),
        })
        result["total_comments_collected"] += len(cd["comments"])

        if cd["comments"]:
            print(f"        ✓ {len(cd['comments'])} comentarios")
            for j, c in enumerate(cd["comments"], 1):
                preview = c["text"][:60] + "…" if len(c["text"]) > 60 else c["text"]
                print(f"           {j}. @{c['username']}: {preview}")
        else:
            print(f"        ⚠ {cd.get('error', 'sin comentarios')}")

        if i < len(posts):
            time.sleep(2)

    result["success"] = True
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

def run_tests(session_id: str = SESSION_ID):
    sep = "─" * 60
    print(f"\n{sep}")
    print("TESTS DE DIAGNÓSTICO")
    print(sep)

    session = _bootstrap_session(session_id)

    csrf = session.cookies.get("csrftoken", "")
    if csrf:
        print(f"\n[T1] ✓ CSRF token: {csrf[:12]}…")
    else:
        print("\n[T1] ⚠ CSRF token no obtenido")

    test_user = "instagram"
    print(f"\n[T2] Detalles de @{test_user}…")
    user = get_user_details(test_user, session)
    if user and user.get("user_id"):
        print(f"       ✓ @{user['username']}  ID={user['user_id']}")
    else:
        print("       ✗ Fallo")
        return

    print(f"\n[T3] Posts de @{test_user} (limit=2)…")
    posts = get_user_posts(test_user, session, limit=2)

    print(f"\n[T4] Comentarios del primer post…")
    first = posts[0]
    cd = get_post_comments(first["media_id"], first["code"], session, limit=3)

    print(f"\n{sep}\nTests completados.\n{sep}\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    username = input("Username de Instagram (sin @): ").strip()
    if not username:
        print(json.dumps({"error": "No se ingresó username"}, indent=2))
        return

    try:
        post_limit = int(input("Número de posts (default 10): ").strip() or "10")
    except ValueError:
        post_limit = 10

    print(f"\n[info] Iniciando sesión…")
    session = _bootstrap_session(SESSION_ID)

    print(f"[info] Scraping @{username}  (posts={post_limit}, comentarios=3)…")
    result = get_posts_with_comments(username, session, post_limit, comment_limit=3)

    if result["success"]:
        filename = f"{username}_data.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        u = result["user_info"]
        print(f"\n✅ Guardado en {filename}")
        print(f"   @{u['username']}  —  {u['follower_count']:,} seguidores")
        print(f"   Posts obtenidos : {len(result['posts'])}")
        print(f"   Comentarios     : {result['total_comments_collected']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        main()
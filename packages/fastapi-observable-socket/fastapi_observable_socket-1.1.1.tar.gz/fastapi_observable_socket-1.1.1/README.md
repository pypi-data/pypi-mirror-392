# fastapi_observable_socket

A tiny, ergonomic **WebSocket router** for FastAPI — designed as the backend counterpart of the
[`ObservableSocket`](https://www.npmjs.com/package/@djanext/observable-socket) TypeScript client.

Together, they offer a minimal, predictable request/response layer for real‑time apps without the complexity of RPC frameworks.

---

## ✨ Features

- Route by `route` (aka `path`) with `uuid` correlation  
- Per‑route hooks: `data_check`, `access`, `hydrate`, `dehydrate`  
- Typed message envelopes (`Request`, `Response`)  
- Graceful error mapping (400/403/404/500)  
- Optional PING→PONG heartbeat  
- Fully compatible with ObservableSocket (JS/TS)

---

## 🚀 Installation

```bash
pip install fastapi-observable-socket
```

Requires FastAPI ≥ 0.115 and Python ≥ 3.11.

---

## 🧭 Message Schema

```jsonc
// Request
{
  "uuid": 123,
  "route": "math/sum",
  "headers": { "x-user": "42" },
  "payload": [1, 2, 3, 4]
}

// Response
{
  "uuid": 123,
  "status": 200,
  "headers": {"unit":"test"},
  "payload": {"sum":10}
}
```

---

## 🧩 Quickstart

```python
from fastapi import FastAPI
from fastapi_observable_socket import SocketRouter, Status

app = FastAPI()
router = SocketRouter()

@router.route("math/sum")
async def sum_handler(ws, headers, payload):
    return {"status": Status.OK, "payload": {"sum": sum(payload or [])}}

app.add_websocket_route("/ws", router)
```

---

## ⚙️ Route Options

Each route can define:

- **data_check(message[, local]) → bool**  
  Early validation. May mutate `local` (a dict) to store lightweight cached values.

- **access(ws, message[, local]) → bool**  
  Access logic. May fetch data (DB, external source) and store it in `local`.

- **hydrate(ws, message) → Any**  
  Builds handler arguments. If defined, it overrides any cached value in `local`.

- **dehydrate(payload) → Any**  
  Final output transformation (serialization, shaping, redaction, etc.).

---

## 🧩 Handler Argument Behavior

Depending on hooks:

| Situation | Handler receives |
|----------|------------------|
| No `hydrate`, no cached data | `(ws, headers, payload)` |
| Cached value stored in `local["value"]` | handler receives that cached value |
| `hydrate` is defined | handler receives hydrate's return value (highest priority) |

General rule:  
> `hydrate` > cached `local` > `(ws, headers, payload)`.

---

## 🔥 Example — Fetch Once, Use Twice

This example shows how to validate, authorize, fetch an article **once**, and reuse it later.

```python
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket
from fastapi_observable_socket import (
    MessageData, SocketRouter, HandlerResult, Status
)

from .models import Article
from .db import get_async_db


app = FastAPI()
router = SocketRouter()


async def data_check_article(message: MessageData, local: dict) -> bool:
    try:
        local["article_id"] = int(message.headers.get("article"))
    except (TypeError, ValueError):
        return False
    return True


async def access_article(ws: WebSocket, message: MessageData, local: dict) -> bool:
    db: AsyncSession = ws.scope["db"]
    article_id = local["article_id"]

    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if article is None:
        local["value"] = None
        return True

    local["value"] = article  # cached for later

    user = ws.scope.get("user")
    if article.access == "PUBLIC":
        return True
    if article.access == "MEMBERS":
        return user is not None
    return article.author == user

async def article_to_json(article:Article) -> dict:
    return {
            "title": article.title,
            "author": article.author.name,
            "body": article.content,
        }


# hydrate is omitted intentionally — cached article will be used
@router.route("get-article", options={
    "data_check": data_check_article,
    "access": access_article,
    "dehydrate": article_to_json
})
async def get_article(local: dict) -> HandlerResult:
    if local["value"] is None:
        return {"status": Status.NOT_FOUND, "payload": {"message": "not found"}}

    return {
        "status": Status.OK,
        "payload": local["value"]
    }


@app.websocket("/ws")
async def websocket_router(ws: WebSocket):
    # Attach DB, user, etc. into ws.scope beforehand
    router(ws)
```

### What happens:

- `data_check_article` validates header & stores `article_id`  
- `access_article` loads the article once, caches it in `local["value"]`, checks access  
- Because no `hydrate` is defined, handler receives the cached article  
- if article is fetched when checking access, `get_article()` returns status 200 and that article, else it returns status 404 and not found message
- if `get_article()` returns status 200 (200 <= status < 300), then the payload part which is the actual article will be sent to `article_to_json()` and serialized there. the result will replace output payload.
---

## 🔢 Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 400 | BAD_REQUEST |
| 403 | FORBIDDEN |
| 404 | NOT_FOUND |
| 500 | INTERNAL_SERVER_ERROR |
| 402 | PENDING |

---

## 🧰 Python Compatibility

| Python | Behavior |
|--------|----------|
| **3.13+** | Uses native `asyncio.Queue.shutdown()` |
| **3.11–3.12** | Uses internal compat shim with sentinel shutdown |

Zero API differences.

---

## 🧠 Why This Package?

| Package | Model | Feature | Client Story |
|---------|--------|----------|--------------|
| **fastapi_observable_socket** | Route + UUID | Lightweight, hookable, ObservableSocket support | JS/TS client |
| fastapi-websocket-rpc | JSON-RPC | Full RPC | Python client |
| fastapi-websocket-pubsub | PubSub | Multicast topics | Python client |
| fastapi-ws-router | Typed events | Pydantic unions | No official client |

A middle ground between raw Starlette WebSockets and heavy RPC systems.

---

## 📦 License

MIT

---

### Related

- Frontend: https://www.npmjs.com/package/@djanext/observable-socket
- Backend: this repository
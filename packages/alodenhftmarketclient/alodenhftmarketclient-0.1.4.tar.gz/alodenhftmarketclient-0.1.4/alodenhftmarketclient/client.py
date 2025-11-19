import asyncio
import contextlib
from dataclasses import dataclass
from typing import Any, AsyncIterator, Awaitable, Callable, Dict, Optional, Sequence

import httpx
import websockets

from .protocol import rfc3339_ms, try_loads

Json = Dict[str, Any]
OnEvent = Callable[[Json], Awaitable[None]] | Callable[[Json], None]

from collections import deque
from typing import Deque, List


@dataclass
class LoginInfo:
    status: str
    user: Optional[str]
    session: Optional[str]


class MarketClient:
    """High-level REST + WebSocket client for the bridge server."""

    def __init__(self, base_url: str, *, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http: Optional[httpx.AsyncClient] = None
        self.user_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self._symbols_cache: Optional[list[Json]] = None
        # Streaming state
        self._md_ws: Optional[websockets.WebSocketClientProtocol] = None
        self._md_task: Optional[asyncio.Task] = None
        self._md_channel_hook: Optional[OnEvent] = None
        self._on_md_event: Optional[OnEvent] = None
        self._unicast_ws: Optional[websockets.WebSocketClientProtocol] = None
        self._unicast_task: Optional[asyncio.Task] = None
        self._unicast_channel_hook: Optional[OnEvent] = None
        self._on_event: Optional[OnEvent] = None
        # Transactions buffer (unicast events)
        self._tx_buf: Deque[Json] = deque(maxlen=1000)

    @classmethod
    async def connect(
        cls,
        base_url: str,
        *,
        connect_md: bool = False,
        md_symbols: Optional[Sequence[str]] = None,
        connect_unicast: bool = False,
        on_md_event: Optional[OnEvent] = None,
        on_unicast_event: Optional[OnEvent] = None,
    ) -> "MarketClient":
        """Convenience constructor that logs in and optionally attaches streams."""
        client = cls(base_url)
        await client.login()
        if connect_md:
            await client.connect_md(symbols=md_symbols, on_event=on_md_event)
        if connect_unicast:
            await client.connect_unicast(on_event=on_unicast_event)
        return client

    async def _http_client(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(base_url=self.base_url, timeout=self._timeout)
        return self._http

    async def aclose(self) -> None:
        await self.disconnect_md()
        await self.disconnect_unicast()
        if self._http is not None:
            await self._http.aclose()
        self._http = None

    async def login(self) -> LoginInfo:
        resp = await self._request("POST", "/login")
        if not isinstance(resp, dict):
            resp = {}
        self.user_id = resp.get("user")
        self.session_id = resp.get("session")
        return LoginInfo(
            status=str(resp.get("status", "")),
            user=self.user_id,
            session=self.session_id,
        )

    async def send(
        self,
        op: str,
        payload: Optional[Json] = None,
        *,
        as_role: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Json:
        """Compatibility wrapper that routes ops to REST endpoints."""
        method, path, params, body = self._resolve_http_request(op, payload or {}, as_role=as_role)
        data = await self._request(method, path, params=params, json=body, timeout=timeout)
        envelope: Json = {
            "type": "response",
            "op": op,
            "status": data.get("status", "ok") if isinstance(data, dict) else "ok",
            "ts": rfc3339_ms(),
            "payload": data,
        }
        return envelope

    async def api_request(
        self,
        op: str,
        payload: Optional[Json] = None,
        *,
        as_role: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Json:
        return await self.send(op, payload, as_role=as_role, timeout=timeout)

    async def get_symbols(self, *, force_refresh: bool = False) -> list[Json]:
        if not force_refresh and isinstance(self._symbols_cache, list):
            return self._symbols_cache
        payload = await self._call("symbols.list", {})
        symbols: list[Json] = []
        if isinstance(payload.get("symbols"), list):
            symbols = [s for s in payload["symbols"] if isinstance(s, dict)]
        self._symbols_cache = symbols
        return symbols

    async def get_book(self, sym: str, *, depth: int = 20, side: str = "both") -> Json:
        return await self._call("book.get", {"sym": sym, "depth": depth, "side": side})

    async def place_order(
        self,
        sym: str,
        *,
        side: str,
        price: Optional[str],
        qty: int,
        tif: str = "GTC",
        type_: str = "limit",
        client_order_id: Optional[str] = None,
    ) -> Json:
        payload: Json = {
            "sym": sym,
            "side": side,
            "type": type_,
            "price": price,
            "qty": qty,
            "tif": tif,
        }
        if client_order_id:
            payload["client_order_id"] = client_order_id
        return await self._call("order.place", payload)

    async def cancel_order(
        self,
        *,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None,
    ) -> Json:
        payload: Json = {}
        if order_id:
            payload["order_id"] = order_id
        if client_order_id:
            payload["client_order_id"] = client_order_id
        return await self._call("order.cancel", payload)

    async def list_orders(self) -> list[Json]:
        payload = await self._call("order.list", {})
        orders = payload.get("orders")
        return orders if isinstance(orders, list) else []

    async def order_history(
        self,
        *,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None,
    ) -> Json:
        args: Json = {}
        if order_id:
            args["order_id"] = order_id
        if client_order_id:
            args["client_order_id"] = client_order_id
        return await self._call("order.history", args)

    async def get_portfolio(self) -> Json:
        return await self._call("portfolio.get", {})

    async def get_candles(
        self,
        sym: str,
        *,
        interval_ms: int,
        since_ns: Optional[int] = None,
        until_ns: Optional[int] = None,
        limit: Optional[int] = None,
        last_full_candle_seq: Optional[int] = None,
    ) -> Json:
        payload: Json = {"sym": sym, "interval_ms": interval_ms}
        if since_ns is not None:
            payload["since_ns"] = since_ns
        if until_ns is not None:
            payload["until_ns"] = until_ns
        if limit is not None:
            payload["limit"] = limit
        if last_full_candle_seq is not None:
            payload["last_full_candle_seq"] = last_full_candle_seq
        return await self._call("candles.get", payload)

    async def connect_md(
        self,
        *,
        symbols: Optional[Sequence[str]] = None,
        on_event: Optional[OnEvent] = None,
    ) -> None:
        await self.disconnect_md()
        params: Dict[str, str] = {}
        if symbols:
            filt = ",".join(sorted({s.upper() for s in symbols if s}))
            if filt:
                params["symbols"] = filt
        url = self._ws_url("/ws/md", params)
        self._md_channel_hook = on_event
        self._md_ws = await websockets.connect(url)
        self._md_task = asyncio.create_task(self._md_reader(), name="md_reader")

    async def disconnect_md(self) -> None:
        task = self._md_task
        self._md_task = None
        if task:
            task.cancel()
            with contextlib.suppress(Exception):
                await task
        await self._close_md_ws()

    async def connect_unicast(
        self,
        *,
        user: Optional[str] = None,
        on_event: Optional[OnEvent] = None,
    ) -> None:
        await self.disconnect_unicast()
        key = user or self.user_id
        if not key:
            raise RuntimeError("Call login() first to obtain a user id")
        url = self._ws_url("/ws/unicast", {"user": key})
        self._unicast_channel_hook = on_event
        self._unicast_ws = await websockets.connect(url)
        self._unicast_task = asyncio.create_task(self._unicast_reader(), name="unicast_reader")

    async def disconnect_unicast(self) -> None:
        task = self._unicast_task
        self._unicast_task = None
        if task:
            task.cancel()
            with contextlib.suppress(Exception):
                await task
        await self._close_unicast_ws()

    def set_event_hook(self, handler: Optional[OnEvent]) -> None:
        """Register a global hook invoked for each unicast event."""
        self._on_event = handler

    def set_md_hook(self, handler: Optional[OnEvent]) -> None:
        """Register a global hook invoked for each MD event."""
        self._on_md_event = handler

    def configure_transactions(self, *, capacity: int = 1000) -> None:
        cap = max(1, int(capacity))
        old: List[Json] = list(self._tx_buf)[-cap:]
        self._tx_buf = deque(old, maxlen=cap)

    def clear_transactions(self) -> None:
        self._tx_buf.clear()

    def get_transactions(self, limit: Optional[int] = None) -> List[Json]:
        if limit is None or limit <= 0:
            return list(self._tx_buf)
        return list(self._tx_buf)[-int(limit):]

    # --- Internal helpers -------------------------------------------------

    async def _call(self, op: str, payload: Optional[Json] = None, *, timeout: Optional[float] = None) -> Json:
        resp = await self.send(op, payload, timeout=timeout or self._timeout)
        out = resp.get("payload")
        return out if isinstance(out, dict) else {}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Json] = None,
        timeout: Optional[float] = None,
    ) -> Json:
        cli = await self._http_client()
        resp = await cli.request(method, path, params=params, json=json, timeout=timeout or self._timeout)
        resp.raise_for_status()
        return resp.json()

    def _resolve_http_request(
        self,
        op: str,
        payload: Json,
        *,
        as_role: Optional[str] = None,
    ) -> tuple[str, str, Optional[Dict[str, Any]], Optional[Json]]:
        if op == "auth.login":
            return "POST", "/login", None, {}
        if op == "symbols.list":
            return "GET", "/symbols", None, None
        if op == "book.get":
            sym = payload.get("sym")
            if not sym:
                raise ValueError("book.get requires 'sym'")
            params: Dict[str, Any] = {}
            if payload.get("depth") is not None:
                params["depth"] = payload["depth"]
            if payload.get("side"):
                params["side"] = payload["side"]
            return "GET", f"/book/{sym}", params or None, None
        if op == "order.place":
            return "POST", "/order.place", None, payload
        if op == "order.cancel":
            if not payload:
                raise ValueError("order.cancel requires order_id or client_order_id")
            return "POST", "/order.cancel", None, payload
        if op == "order.list":
            return "GET", "/orders", None, None
        if op == "order.history":
            qs = {k: v for k, v in payload.items() if v is not None}
            if not qs:
                raise ValueError("order.history requires order_id or client_order_id")
            return "GET", "/order.history", qs, None
        if op == "portfolio.get":
            return "GET", "/portfolio", None, None
        if op == "candles.get":
            qs = {k: v for k, v in payload.items() if v is not None}
            return "GET", "/candles", qs, None
        if op.startswith("admin."):
            if as_role != "admin":
                raise ValueError("admin ops require as_role='admin'")
            suffix = op.split(".", 1)[1]
            return "POST", f"/admin/{suffix}", None, payload
        raise ValueError(f"Unsupported op: {op}")

    async def _md_reader(self) -> None:
        assert self._md_ws is not None
        try:
            async for msg in self._md_ws:
                evt = try_loads(msg)
                if evt is None:
                    continue
                await self._fanout_md(evt)
        except Exception:
            pass
        finally:
            await self._close_md_ws()
            self._md_task = None

    async def _unicast_reader(self) -> None:
        assert self._unicast_ws is not None
        try:
            async for msg in self._unicast_ws:
                evt = try_loads(msg)
                if evt is None:
                    continue
                self._store_transaction(evt)
                await self._fanout_unicast(evt)
        except Exception:
            pass
        finally:
            await self._close_unicast_ws()
            self._unicast_task = None

    async def _fanout_md(self, evt: Json) -> None:
        for cb in (self._on_md_event, self._md_channel_hook):
            if cb is None:
                continue
            try:
                res = cb(evt)
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

    async def _fanout_unicast(self, evt: Json) -> None:
        for cb in (self._on_event, self._unicast_channel_hook):
            if cb is None:
                continue
            try:
                res = cb(evt)
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

    def _store_transaction(self, evt: Json) -> None:
        if isinstance(evt, dict):
            try:
                self._tx_buf.append(evt)
            except Exception:
                pass

    def _ws_url(self, path: str, params: Optional[Dict[str, str]] = None) -> str:
        base = self.base_url
        if base.startswith("https://"):
            scheme = "wss://"
            rest = base[len("https://") :]
        elif base.startswith("http://"):
            scheme = "ws://"
            rest = base[len("http://") :]
        else:
            scheme = "ws://"
            rest = base
        if not path.startswith("/"):
            path = "/" + path
        query = ""
        if params:
            from urllib.parse import urlencode

            encoded = urlencode(params)
            if encoded:
                query = f"?{encoded}"
        return f"{scheme}{rest}{path}{query}"

    async def _close_md_ws(self) -> None:
        ws = self._md_ws
        self._md_ws = None
        self._md_channel_hook = None
        if ws:
            with contextlib.suppress(Exception):
                await ws.close()

    async def _close_unicast_ws(self) -> None:
        ws = self._unicast_ws
        self._unicast_ws = None
        self._unicast_channel_hook = None
        if ws:
            with contextlib.suppress(Exception):
                await ws.close()


class MdStream:
    """Lightweight async iterator for raw MD WebSocket messages."""

    def __init__(self, ws: websockets.WebSocketClientProtocol):
        self._ws = ws
        self._closed = False

    def __aiter__(self) -> AsyncIterator[Json]:
        return self._iter()

    async def _iter(self) -> AsyncIterator[Json]:
        try:
            async for msg in self._ws:
                o = try_loads(msg)
                if isinstance(o, dict):
                    yield o
        finally:
            await self.close()

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        with contextlib.suppress(Exception):
            await self._ws.close()

    async def __aenter__(self) -> "MdStream":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

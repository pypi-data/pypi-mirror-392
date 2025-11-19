import asyncio
import socket
import struct
import time
from collections import deque
from dataclasses import dataclass
from typing import Awaitable, Callable, Deque, Dict, Optional

ORDER_FMT = "<QQIBBBBqqQQQ"  # 64 bytes total - matches C++ OrderFrame struct
ORDER_SIZE = struct.calcsize(ORDER_FMT)  # Should be 64

EventHandler = Callable[[bytes], Awaitable[None]]


@dataclass
class GatewayConfig:
    host: str = "127.0.0.1"
    port: int = 9001


@dataclass
class MarketDataConfig:
    host: str = "127.0.0.1"
    port: int = 5001


class ExchangeClient:
    def __init__(
        self,
        team_token: str,
        gateway: GatewayConfig | None = None,
        market_data: MarketDataConfig | None = None,
    ) -> None:
        self.team_token = team_token
        self.gateway = gateway or GatewayConfig()
        self.market_data = market_data or MarketDataConfig()
        self._tcp_writer: Optional[asyncio.StreamWriter] = None
        self._handlers: Dict[str, EventHandler] = {}
        self._order_id = 1
        self._md_running = False
        self._md_queue: Deque[bytes] = deque()
        self._tcp_reader: Optional[asyncio.StreamReader] = None
        self._response_task: Optional[asyncio.Task] = None
        self._last_flush = time.time()
        self._pending_orders = 0
    def on(self, event: str, handler: EventHandler) -> None:
        self._handlers[event] = handler

    async def connect(self) -> None:
        reader, writer = await asyncio.open_connection(
            self.gateway.host,
            self.gateway.port,
        )
        self._tcp_reader = reader
        self._tcp_writer = writer
        writer.write(self.team_token.encode() + b"\n")
        await writer.drain()
        await reader.readline()

        loop = asyncio.get_running_loop()
        self._md_transport, _ = await loop.create_datagram_endpoint(
            lambda: _MDProtocol(self._enqueue_md),
            remote_addr=(self.market_data.host, self.market_data.port),
        )
        self._md_running = True
        asyncio.create_task(self._process_md())
        
        # Start reading order responses to prevent socket buffer overflow
        self._response_task = asyncio.create_task(self._read_responses())

    async def close(self) -> None:
        self._md_running = False
        if self._response_task:
            self._response_task.cancel()
        if hasattr(self, "_md_transport"):
            self._md_transport.close()
        if self._tcp_writer:
            self._tcp_writer.close()
            await self._tcp_writer.wait_closed()

    async def send_new_async(
        self,
        client_id: int,
        symbol_id: int,
        side: int,
        price_ticks: int,
        quantity: int,
        ord_type: int = 0,
        tif: int = 0,
    ) -> int:
        """Async version that immediately flushes to network. Returns order_id."""
        if not self._tcp_writer:
            raise RuntimeError("connect() must be called before send_new()")
        order_id = self._order_id
        frame = struct.pack(
            ORDER_FMT,
            client_id,       # u64
            order_id,        # u64
            symbol_id,       # u32
            side,            # u8
            ord_type,        # u8
            tif,             # u8
            0,               # u8 - msg_type (0=NEW)
            price_ticks,     # i64
            quantity,        # i64
            time.time_ns(),  # u64 - timestamp
            0,               # u64 - reserved
            0,               # u64 - crc_or_sig
        )
        self._order_id += 1
        self._tcp_writer.write(frame)
        await self._tcp_writer.drain()
        return order_id  # CRITICAL: Actually send it!
    
    async def cancel_order_async(
        self,
        client_id: int,
        order_id: int,
        symbol_id: int,
    ) -> None:
        """Cancel an order by client_id and order_id."""
        if not self._tcp_writer:
            raise RuntimeError("connect() must be called before cancel_order()")
        frame = struct.pack(
            ORDER_FMT,
            client_id,       # u64
            order_id,        # u64 - REQUIRED for matching engine lookup
            symbol_id,       # u32
            0,               # u8 - side (not used)
            0,               # u8 - ord_type (not used)
            0,               # u8 - tif (not used)
            1,               # u8 - msg_type (1=CANCEL)
            0,               # i64 - price (not used)
            0,               # i64 - quantity (not used)
            time.time_ns(),  # u64 - timestamp
            0,               # u64 - reserved
            0,               # u64 - crc_or_sig
        )
        self._tcp_writer.write(frame)
        await self._tcp_writer.drain()
    
    def send_new(
        self,
        client_id: int,
        symbol_id: int,
        side: int,
        price_ticks: int,
        quantity: int,
        ord_type: int = 0,
        tif: int = 0,
    ) -> None:
        if not self._tcp_writer:
            raise RuntimeError("connect() must be called before send_new()")
        frame = struct.pack(
            ORDER_FMT,
            client_id,       # u64
            self._order_id,  # u64
            symbol_id,       # u32
            side,            # u8
            ord_type,        # u8
            tif,             # u8
            0,               # u8 - msg_type (0=NEW)
            price_ticks,     # i64
            quantity,        # i64
            time.time_ns(),  # u64 - timestamp
            0,               # u64 - reserved
            0,               # u64 - crc_or_sig
        )
        self._order_id += 1
        self._tcp_writer.write(frame)
        self._pending_orders += 1
        
        # Auto-flush every 100 orders OR every 1 second
        now = time.time()
        if self._pending_orders >= 100 or (now - self._last_flush) >= 1.0:
            # Schedule a flush on the event loop
            asyncio.create_task(self._auto_flush())
    
    async def _auto_flush(self) -> None:
        """Automatically flush buffered orders to network."""
        if self._tcp_writer and self._pending_orders > 0:
            try:
                await self._tcp_writer.drain()
                self._pending_orders = 0
                self._last_flush = time.time()
            except Exception:
                pass  # Connection may be closing

    async def _process_md(self) -> None:
        while self._md_running:
            if not self._md_queue:
                await asyncio.sleep(0.01)
                continue
            frame = self._md_queue.popleft()
            chan_id = int.from_bytes(frame[:4], "little")
            if chan_id == 1:
                handler = self._handlers.get("trade")
            elif chan_id == 2:
                handler = self._handlers.get("top")
            else:
                handler = self._handlers.get("depth")
            if handler:
                await handler(frame)

    def _enqueue_md(self, data: bytes) -> None:
        self._md_queue.append(data)
    
    async def _drain_once(self) -> None:
        """Drain writer once to actually send buffered data."""
        if self._tcp_writer:
            try:
                await asyncio.wait_for(self._tcp_writer.drain(), timeout=2.0)
            except asyncio.TimeoutError:
                print("Warning: Socket drain timeout (network slow)")
            except Exception as e:
                # Don't spam errors, but log occasionally
                pass
    
    async def _read_responses(self) -> None:
        """Continuously read order response frames from gateway."""
        if not self._tcp_reader:
            print("WARNING: _read_responses called but no TCP reader available")
            return
        
        RESPONSE_SIZE = 64  # Response frames are 64 bytes
        
        try:
            while True:
                try:
                    frame = await self._tcp_reader.readexactly(RESPONSE_SIZE)
                    # Successfully read a response - just discard it for now
                    # In a real implementation, you'd parse and handle these
                except asyncio.IncompleteReadError as e:
                    # Connection closed by server
                    if len(e.partial) == 0:
                        print("INFO: Gateway closed connection (normal for end of round)")
                        break
                    else:
                        print(f"WARNING: Incomplete response frame: got {len(e.partial)} bytes, expected {RESPONSE_SIZE}")
                        continue
        except (ConnectionResetError, EOFError) as e:
            print(f"INFO: Connection closed: {type(e).__name__}")
        except asyncio.CancelledError:
            # Normal shutdown - don't print anything
            pass
        except Exception as e:
            print(f"ERROR in _read_responses: {type(e).__name__}: {e}")


class _MDProtocol(asyncio.DatagramProtocol):
    def __init__(self, on_datagram: Callable[[bytes], None]) -> None:
        self.on_datagram = on_datagram

    def datagram_received(self, data: bytes, _: tuple[str, int] | None) -> None:
        self.on_datagram(data)

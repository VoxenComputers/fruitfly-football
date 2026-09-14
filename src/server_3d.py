"""Lightweight HTTP & SSE Streaming Server for 3D Drosophila Flight Arena.

Serves the WebGL 3D visualizer from web/ and streams real-time neural spikes
and motor commands to connected browsers via Server-Sent Events (SSE).
Uses Python standard library only (zero external server dependencies).
"""

from __future__ import annotations

import os
import json
import time
import queue
import logging
import threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver
from typing import Optional, Dict, Any

logger = logging.getLogger("3DArenaServer")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [3D Server]: %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

# Thread-safe queue list for connected SSE browser clients
_clients: list[queue.Queue] = []
_clients_lock = threading.Lock()


def broadcast_telemetry(payload: Dict[str, Any]):
    """Broadcasts a telemetry packet to all connected 3D browser clients."""
    with _clients_lock:
        data_str = f"data: {json.dumps(payload)}\n\n"
        dead = []
        for q in _clients:
            try:
                q.put_nowait(data_str)
            except queue.Full:
                dead.append(q)
        for d in dead:
            _clients.remove(d)


class ArenaHTTPHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving web/ static assets and /api/stream SSE."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/api/stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            client_q = queue.Queue(maxsize=100)
            with _clients_lock:
                _clients.append(client_q)
            logger.info(f"New 3D Web client connected. Total active clients: {len(_clients)}")

            try:
                while True:
                    try:
                        msg = client_q.get(timeout=1.0)
                        self.wfile.write(msg.encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        # Heartbeat keepalive ping
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                with _clients_lock:
                    if client_q in _clients:
                        _clients.remove(client_q)
                logger.info("3D Web client disconnected.")
            return

        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        # Default static file serving from web/
        return super().do_GET()

    def log_message(self, format, *args):
        # Suppress routine static asset GET logs for clean console
        try:
            if args and isinstance(args[0], str) and "/api/stream" in args[0]:
                return
        except Exception:
            pass
        logger.debug("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def start_3d_server(port: int = 8080) -> ThreadedHTTPServer:
    """Starts the 3D Web server in a background daemon thread."""
    server = None
    for p in [port, port + 1, port + 2, 8000, 8888]:
        try:
            server = ThreadedHTTPServer(("0.0.0.0", p), ArenaHTTPHandler)
            actual_port = p
            break
        except OSError:
            continue

    if server is None:
        raise RuntimeError(f"Could not bind 3D server to port {port} or adjacent ports.")

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    logger.info(f"3D Fly Flight Arena server running at http://localhost:{actual_port}")
    return server

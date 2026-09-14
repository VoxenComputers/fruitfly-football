"""Unit tests for 3D WebGL Server & Telemetry Broadcast."""

import time
import urllib.request
import pytest
from src.server_3d import start_3d_server, broadcast_telemetry


def test_server_3d_startup_and_static_files():
    """Verify that the 3D server serves web/ assets properly."""
    server = start_3d_server(port=8090)
    port = server.server_address[1]

    try:
        # 1. Fetch index.html
        url = f"http://127.0.0.1:{port}/index.html"
        req = urllib.request.urlopen(url, timeout=3.0)
        assert req.status == 200
        content = req.read().decode("utf-8")
        assert "Drosophila" in content
        assert "Three.js" in content or "three.min.js" in content

        # 2. Fetch styles.css
        css_url = f"http://127.0.0.1:{port}/styles.css"
        css_req = urllib.request.urlopen(css_url, timeout=3.0)
        assert css_req.status == 200
        css_content = css_req.read().decode("utf-8")
        assert "hud-header" in css_content

        # 3. Test telemetry broadcast doesn't crash without clients
        broadcast_telemetry({
            "action": "SWIPE_LEFT",
            "spikes": 120,
            "voltage": 0.45,
            "motor_rates": {"left": 0.8},
            "optic_flow": {"left": 0.5},
        })
    finally:
        server.shutdown()
        server.server_close()

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SERVER_PATH = (Path(__file__).parent.parent / "src" / "mcp_server.py").resolve()


INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "pytest", "version": "0.1"},
    },
}

INITED = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}


def _send(p: subprocess.Popen, obj: dict) -> None:
    p.stdin.write((json.dumps(obj) + "\n").encode())
    p.stdin.flush()


def _read_json_line(p: subprocess.Popen, timeout: float = 10.0) -> dict:
    end = time.time() + timeout
    while time.time() < end:
        line = p.stdout.readline()
        if not line:
            continue
        s = line.decode(errors="ignore").strip()
        try:
            return json.loads(s)
        except Exception:
            # Skip non-JSON log lines
            continue
    raise AssertionError("Timed out waiting for JSON-RPC response")


def test_mcp_initialize_and_tools_list():
    assert SERVER_PATH.exists(), f"Server not found at {SERVER_PATH}"

    env = os.environ.copy()
    # Ensure project root on PYTHONPATH for imports
    repo_root = Path(__file__).parents[3]
    server_src = repo_root / "heroes-platform" / "mcp_server" / "src"
    proj_src = repo_root / "src"
    env["PYTHONPATH"] = f"{server_src}:{proj_src}:{env.get('PYTHONPATH', '')}"

    p = subprocess.Popen(
        [sys.executable, str(SERVER_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(server_src),  # avoid shadowing stdlib 'platform' by project folder
    )
    try:
        _send(p, INIT)
        init_resp = _read_json_line(p)
        assert init_resp.get("result", {}).get("protocolVersion") == "2024-11-05"

        _send(p, INITED)

        _send(p, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        list_resp = _read_json_line(p)
        tools = {t["name"] for t in list_resp.get("result", {}).get("tools", [])}
        required = {
            "server_info",
            "standards_list",
            "standards_get",
            "standards_search",
            "workflow_integration",
            "registry_compliance_check",
        }
        missing = required - tools
        assert not missing, f"Missing tools: {sorted(missing)}"

        # Smoke-call server_info
        _send(
            p,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "server_info", "arguments": {}},
            },
        )
        info_resp = _read_json_line(p)
        assert "result" in info_resp

        # Smoke-call standards_list
        _send(
            p,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "standards_list", "arguments": {}},
            },
        )
        list_call_resp = _read_json_line(p)
        res_obj = list_call_resp.get("result", {})
        payload = res_obj.get("structuredContent", {}).get("result") or (
            res_obj.get("content") or [{}]
        )[0].get("text")
        assert payload, f"No payload in tools/call response: {res_obj}"
        data = json.loads(payload)
        assert isinstance(data.get("total_count"), int)
        assert isinstance(data.get("standards"), list)
    finally:
        p.kill()

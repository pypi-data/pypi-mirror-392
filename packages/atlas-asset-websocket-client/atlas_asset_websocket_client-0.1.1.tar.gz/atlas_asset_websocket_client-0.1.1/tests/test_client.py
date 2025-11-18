import json
from datetime import datetime, timezone
from typing import Any, Iterable, List

import pytest
from atlas_asset_ws_client.client import AssetWebSocketClient
from atlas_asset_ws_client.schemas import AssetEnvelope, AssetMeta


class DummyConnection:
    """Minimal async websocket stub used by the tests."""

    def __init__(self, responses: Iterable[Any] | None = None) -> None:
        self.sent: List[Any] = []
        self.closed = False
        self._responses = list(responses or [])

    async def send(self, data: Any) -> None:
        self.sent.append(data)

    async def recv(self) -> Any:
        if not self._responses:
            raise RuntimeError("No queued responses available")
        return self._responses.pop(0)

    async def close(self) -> None:
        self.closed = True


def _server_envelope(
    message_type: str,
    *,
    stream: str,
    payload: dict[str, Any] | None = None,
) -> AssetEnvelope:
    meta = AssetMeta(
        asset_id="asset-123",
        stream=stream,
        sent_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        correlation_id="server-correlation",
    )
    return AssetEnvelope(type=message_type, meta=meta, payload=payload or {"status": "ok"})


@pytest.mark.asyncio
async def test_connect_is_idempotent_and_close_is_graceful() -> None:
    connection = DummyConnection()

    async def fake_connect(url: str):
        assert url == "wss://atlas.test/asset"
        return connection

    client = AssetWebSocketClient("wss://atlas.test/asset", "asset-123", connect=fake_connect)

    await client.connect()
    await client.connect()

    assert client.is_connected is True
    assert len(connection.sent) == 0  # no traffic yet

    await client.close()
    assert connection.closed is True
    assert client.is_connected is False

    # Closing again without an active connection should be a no-op
    await client.close()


@pytest.mark.asyncio
async def test_receive_json_handles_strings_bytes_and_dicts() -> None:
    responses = [
        json.dumps({"first": 1}),
        b'{"second": 2}',
        {"third": 3},
    ]
    connection = DummyConnection(responses)

    async def fake_connect(url: str):
        return connection

    client = AssetWebSocketClient("wss://atlas.test/asset", "asset-123", connect=fake_connect)
    await client.connect()

    assert await client.receive_json() == {"first": 1}
    assert await client.receive_json() == {"second": 2}
    assert await client.receive_json() == {"third": 3}


@pytest.mark.asyncio
async def test_handshake_sends_envelope_and_skips_connection_ack() -> None:
    ack = _server_envelope("system:handshake:ack", stream="system")
    responses = [
        json.dumps({"type": "connection", "status": "ok"}),
        json.dumps(ack.model_dump(mode="json")),
    ]
    connection = DummyConnection(responses)

    async def fake_connect(url: str):
        return connection

    client = AssetWebSocketClient("wss://atlas.test/asset", "asset-XYZ", connect=fake_connect)

    custom_sent_at = datetime(2024, 5, 17, 12, 0, tzinfo=timezone.utc)
    await client.connect()
    result = await client.handshake(
        payload={"status": "ready"},
        correlation_id="corr-123",
        sent_at=custom_sent_at,
    )

    assert result == ack

    sent_payload = json.loads(connection.sent[0])
    assert sent_payload["type"] == "system:handshake"
    assert sent_payload["payload"]["status"] == "ready"
    assert sent_payload["meta"]["correlation_id"] == "corr-123"
    serialized_sent_at = sent_payload["meta"]["sent_at"]
    parsed_sent_at = datetime.fromisoformat(serialized_sent_at.replace("Z", "+00:00"))
    assert parsed_sent_at == custom_sent_at


@pytest.mark.asyncio
async def test_complete_command_merges_defaults_and_waits_for_ack() -> None:
    ack = _server_envelope("command:complete:ack", stream="commands")
    responses = [json.dumps(ack.model_dump(mode="json"))]
    connection = DummyConnection(responses)

    async def fake_connect(url: str):
        return connection

    client = AssetWebSocketClient("wss://atlas.test/asset", "asset-XYZ", connect=fake_connect)

    await client.connect()
    result = await client.complete_command(
        command_id="CMD-1",
        queue_index=5,
        status="success",
        result={"detail": "ok"},
    )

    assert result == ack

    sent_payload = json.loads(connection.sent[-1])
    assert sent_payload["type"] == "command:complete"
    assert sent_payload["payload"]["command_id"] == "CMD-1"
    assert sent_payload["payload"]["index"] == 5
    assert sent_payload["payload"]["queue_index"] == 5
    assert sent_payload["payload"]["status"] == "success"
    assert sent_payload["payload"]["result"] == {"detail": "ok"}

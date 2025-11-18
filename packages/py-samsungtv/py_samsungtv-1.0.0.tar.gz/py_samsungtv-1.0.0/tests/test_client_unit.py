from __future__ import annotations

from typing import Any, List, Mapping, cast

import pytest

from samsungtv import (
    ArtMode,
    InputSource,
    MuteState,
    PowerState,
    SamsungTVAuthenticationError,
    SamsungTVClient,
)


class FakeConnection:
    """Simple in-memory transport used for unit tests."""

    def __init__(self, responses: list[Mapping[str, Any]]) -> None:
        self.responses = responses
        self.requests: List[Mapping[str, Any]] = []

    async def request(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        self.requests.append(payload)
        if not self.responses:
            raise AssertionError("No fake response queued")
        return self.responses.pop(0)

    async def close(self) -> None:  # pragma: no cover - unused
        return None


@pytest.mark.asyncio
async def test_create_access_token_updates_state() -> None:
    fake = FakeConnection([{"result": {"AccessToken": "abc"}}])
    client = SamsungTVClient("example.com")
    client._connection = cast(Any, fake)

    token = await client.create_access_token()

    assert token == "abc"
    assert client.access_token == "abc"
    assert fake.requests[0]["method"] == "createAccessToken"
    assert "params" not in fake.requests[0]


@pytest.mark.asyncio
async def test_get_tv_states_sends_token() -> None:
    fake = FakeConnection([{"result": {"power": "powerOff"}}])
    client = SamsungTVClient("example.com", access_token="secret-token")
    client._connection = cast(Any, fake)

    states = await client.get_tv_states()

    assert states["power"] == PowerState.POWER_OFF
    payload = fake.requests[0]
    assert payload["method"] == "getTVStates"
    assert payload["params"]["AccessToken"] == "secret-token"


@pytest.mark.asyncio
async def test_direct_channel_control_requires_channel_meta() -> None:
    fake = FakeConnection([{"result": {"channelNum": "1-1"}}])
    client = SamsungTVClient("example.com", access_token="token")
    client._connection = cast(Any, fake)

    with pytest.raises(ValueError):
        await client.direct_channel_control(channel_num="2-1")


@pytest.mark.asyncio
async def test_missing_token_raises() -> None:
    client = SamsungTVClient("example.com")
    client._connection = cast(Any, FakeConnection([]))

    with pytest.raises(SamsungTVAuthenticationError):
        await client.get_tv_states()


@pytest.mark.asyncio
async def test_custom_port_propagates() -> None:
    fake = FakeConnection([{"result": {"power": "powerOn"}}])
    client = SamsungTVClient("example.com", port=1515, access_token="tok")
    client._connection = cast(Any, fake)

    await client.get_tv_states()

    payload = fake.requests[0]
    assert payload["id"] == 1  # sanity check request path still works
    assert client._port == 1515


@pytest.mark.asyncio
async def test_art_mode_helpers() -> None:
    fake = FakeConnection(
        [{"result": {"artMode": "artModeOn"}}, {"result": {"artMode": "artModeOff"}}]
    )
    client = SamsungTVClient("example.com", access_token="tok")
    client._connection = cast(Any, fake)

    on_state = await client.art_mode_on()
    off_state = await client.art_mode_off()

    assert on_state is ArtMode.ART_MODE_ON
    assert off_state is ArtMode.ART_MODE_OFF
    assert fake.requests[0]["method"] == "artModeControl"
    assert fake.requests[1]["params"]["artMode"] == ArtMode.ART_MODE_OFF


@pytest.mark.asyncio
async def test_select_input_source_alias() -> None:
    fake = FakeConnection([{"result": {"inputSource": "HDMI1"}}])
    client = SamsungTVClient("example.com", access_token="tok")
    client._connection = cast(Any, fake)

    source = await client.select_input_source(InputSource.HDMI1)

    assert source is InputSource.HDMI1
    payload = fake.requests[0]
    assert payload["method"] == "inputSourceControl"
    assert payload["params"]["inputSource"] == InputSource.HDMI1


@pytest.mark.asyncio
async def test_mute_helpers() -> None:
    fake = FakeConnection(
        [{"result": {"mute": "muteOn"}}, {"result": {"mute": "muteOff"}}]
    )
    client = SamsungTVClient("example.com", access_token="tok")
    client._connection = cast(Any, fake)

    assert await client.mute() is MuteState.MUTE_ON
    assert await client.unmute() is MuteState.MUTE_OFF

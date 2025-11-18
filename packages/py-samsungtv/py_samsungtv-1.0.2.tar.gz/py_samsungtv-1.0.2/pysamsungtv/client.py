"""Async client for the Samsung HTTPS JSON-RPC endpoint on port 1516."""

from __future__ import annotations

import inspect
from enum import StrEnum
from types import TracebackType
from typing import Any, Mapping, MutableMapping, Sequence, TypeVar, cast

from .const import DEFAULT_HEADERS, DEFAULT_PORT, JSONRPC_VERSION
from .connection import SamsungTVConnection
from .enums import (
    AirCable,
    ApplicationName,
    ArtMode,
    AtvDtv,
    ChannelAdjust,
    InputSource,
    MuteState,
    PictureMode,
    PictureSize,
    PowerState,
    RemoteKey,
    SoundMode,
    SpeakerSelect,
    VolumeAdjust,
)
from .exceptions import (
    SamsungTVAuthenticationError,
    SamsungTVProtocolError,
    SamsungTVResponseError,
)
from .types import (
    DeviceInfo,
    DirectAccessApp,
    JSONValue,
    TVStates,
    UpdateCallback,
    VideoStates,
)

EnumT = TypeVar("EnumT", bound=StrEnum)


class SamsungTVClient:
    """Async client that wraps the Samsung port 1516 JSON-RPC interface."""

    def __init__(
        self,
        host: str,
        *,
        port: int | None = None,
        verify_ssl: bool = False,
        request_timeout: float = 10.0,
        access_token: str | None = None,
        on_update: UpdateCallback | None = None,
    ) -> None:
        self._host = host
        self._port = port or DEFAULT_PORT
        self._access_token = access_token
        self._on_update = on_update
        self._connection = SamsungTVConnection(
            host,
            port=self._port,
            verify_ssl=verify_ssl,
            request_timeout=request_timeout,
            headers=DEFAULT_HEADERS,
        )
        self._request_id = 0

    async def __aenter__(self) -> SamsungTVClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await self._connection.close()

    @property
    def access_token(self) -> str | None:
        return self._access_token

    def set_update_callback(self, callback: UpdateCallback | None) -> None:
        self._on_update = callback

    def set_access_token(self, token: str | None) -> None:
        self._access_token = token

    async def create_access_token(self) -> str:
        result = await self._request("createAccessToken", include_token=False)
        mapping = self._cast_mapping(result)
        access_token = mapping.get("AccessToken")
        if not isinstance(access_token, str):
            raise SamsungTVProtocolError(
                "createAccessToken returned an unexpected payload"
            )
        self._access_token = access_token
        return access_token

    async def get_tv_states(self) -> TVStates:
        result = await self._request("getTVStates")
        mapping = self._cast_mapping(result)
        states: dict[str, Any] = {}
        self._assign_enum_field(states, mapping, "power", PowerState)
        self._assign_enum_field(states, mapping, "mute", MuteState)
        self._assign_enum_field(states, mapping, "atvDtv", AtvDtv)
        self._assign_enum_field(states, mapping, "airCable", AirCable)
        self._assign_enum_field(states, mapping, "inputSource", InputSource)
        self._assign_enum_field(states, mapping, "pictureMode", PictureMode)
        self._assign_enum_field(states, mapping, "artMode", ArtMode)
        self._assign_str_field(states, mapping, "channelNum")
        return cast(TVStates, states)

    async def get_video_states(self) -> VideoStates:
        result = await self._request("getVideoStates")
        mapping = self._cast_mapping(result)
        states: dict[str, Any] = {}
        for key in ("volume", "contrast", "brightness", "sharpness", "color", "tint"):
            self._assign_int_field(states, mapping, key)
        self._assign_enum_field(states, mapping, "pictureSize", PictureSize)
        self._assign_enum_field(states, mapping, "soundMode", SoundMode)
        self._assign_enum_field(states, mapping, "speakerSelect", SpeakerSelect)
        return cast(VideoStates, states)

    async def power_control(self, power: PowerState | None = None) -> PowerState:
        params: dict[str, Any] = {}
        if power is not None:
            params["power"] = power
        result = await self._request("powerControl", params or None)
        value = self._cast_mapping(result).get("power")
        if value is None:
            raise SamsungTVProtocolError(
                "powerControl payload did not include a power field"
            )
        return self._coerce_enum(value, PowerState)

    async def direct_volume_control(self, volume: int) -> int:
        result = await self._request("directVolumeControl", {"volume": volume})
        value = self._cast_mapping(result).get("volume")
        return int(value if isinstance(value, int) else volume)

    async def volume_up_down(self, action: VolumeAdjust) -> VolumeAdjust:
        result = await self._request("volumeUpDnControl", {"control": action})
        value = self._cast_mapping(result).get("control")
        if value is None:
            raise SamsungTVProtocolError(
                "volumeUpDnControl returned an unexpected control value"
            )
        return self._coerce_enum(value, VolumeAdjust)

    async def mute_control(self, state: MuteState) -> MuteState:
        result = await self._request("muteControl", {"mute": state})
        value = self._cast_mapping(result).get("mute")
        if value is None:
            raise SamsungTVProtocolError(
                "muteControl returned an unexpected mute value"
            )
        return self._coerce_enum(value, MuteState)

    async def channel_up_down(self, action: ChannelAdjust) -> ChannelAdjust:
        result = await self._request("channelUpDnControl", {"control": action})
        value = self._cast_mapping(result).get("control")
        if value is None:
            raise SamsungTVProtocolError(
                "channelUpDnControl returned an unexpected control value"
            )
        return self._coerce_enum(value, ChannelAdjust)

    async def direct_channel_control(
        self,
        *,
        atv_dtv: AtvDtv | None = None,
        air_cable: AirCable | None = None,
        channel_num: str | None = None,
    ) -> str:
        params: dict[str, Any] = {}
        if channel_num is not None:
            if atv_dtv is None or air_cable is None:
                raise ValueError("Setting a channel requires atv_dtv and air_cable")
            params.update(
                {"atvDtv": atv_dtv, "airCable": air_cable, "channelNum": channel_num}
            )
        result = await self._request("directChannelControl", params or None)
        channel = self._cast_mapping(result).get("channelNum")
        if not isinstance(channel, str):
            raise SamsungTVProtocolError(
                "directChannelControl missing channelNum in response"
            )
        return channel

    async def input_source_control(self, source: InputSource) -> InputSource:
        result = await self._request("inputSourceControl", {"inputSource": source})
        value = self._cast_mapping(result).get("inputSource")
        if value is None:
            raise SamsungTVProtocolError(
                "inputSourceControl missing inputSource in response"
            )
        return self._coerce_enum(value, InputSource)

    async def usb_source_control(
        self, device_id: str | None = None, device_name: str | None = None
    ) -> list[DeviceInfo]:
        params: dict[str, Any] | None = None
        if device_id is not None and device_name is not None:
            params = {"deviceId": device_id, "deviceName": device_name}
        result = await self._request("USBSourceControl", params)
        return self._cast_device_list(result)

    async def rvu_source_control(
        self, device_id: str | None = None, device_name: str | None = None
    ) -> list[DeviceInfo]:
        params: dict[str, Any] | None = None
        if device_id is not None and device_name is not None:
            params = {"deviceId": device_id, "deviceName": device_name}
        result = await self._request("RVUSourceControl", params)
        return self._cast_device_list(result)

    async def external_speaker_control(
        self, device_id: str | None = None, device_name: str | None = None
    ) -> list[DeviceInfo]:
        params: dict[str, Any] | None = None
        if device_id is not None and device_name is not None:
            params = {"deviceId": device_id, "deviceName": device_name}
        result = await self._request("externalSpeakerControl", params)
        return self._cast_device_list(result)

    async def direct_access_control(
        self, application: DirectAccessApp, url: str | None = None
    ) -> str:
        params: dict[str, Any] = {"applicationName": application}
        if url is not None:
            params["url"] = url
        result = await self._request("directAccessControl", params)
        value = self._cast_mapping(result).get("applicationName")
        if not isinstance(value, str):
            raise SamsungTVProtocolError(
                "directAccessControl missing applicationName in response"
            )
        return value

    async def remote_key_control(self, key: RemoteKey) -> None:
        await self._request("remoteKeyControl", {"remoteKey": key})

    async def picture_mode_control(self, mode: PictureMode) -> PictureMode:
        result = await self._request("pictureModeControl", {"pictureMode": mode})
        value = self._cast_mapping(result).get("pictureMode")
        if value is None:
            raise SamsungTVProtocolError(
                "pictureModeControl missing pictureMode in response"
            )
        return self._coerce_enum(value, PictureMode)

    async def art_mode_control(self, mode: ArtMode) -> ArtMode:
        result = await self._request("artModeControl", {"artMode": mode})
        value = self._cast_mapping(result).get("artMode")
        if value is None:
            raise SamsungTVProtocolError("artModeControl missing artMode in response")
        return self._coerce_enum(value, ArtMode)

    async def art_mode_on(self) -> ArtMode:
        """Enable art mode on Frame TVs."""

        return await self.art_mode_control(ArtMode.ART_MODE_ON)

    async def art_mode_off(self) -> ArtMode:
        """Disable art mode on Frame TVs."""

        return await self.art_mode_control(ArtMode.ART_MODE_OFF)

    async def contrast_control(self, value: int) -> Mapping[str, Any]:
        result = await self._request("contrastControl", {"contrast": value})
        return self._cast_mapping(result)

    async def brightness_control(self, value: int) -> Mapping[str, Any]:
        result = await self._request("brightnessControl", {"brightness": value})
        return self._cast_mapping(result)

    async def sharpness_control(self, value: int) -> Mapping[str, Any]:
        result = await self._request("sharpnessControl", {"sharpness": value})
        return self._cast_mapping(result)

    async def color_control(self, value: int) -> Mapping[str, Any]:
        result = await self._request("colorControl", {"color": value})
        return self._cast_mapping(result)

    async def tint_control(self, value: int) -> Mapping[str, Any]:
        result = await self._request("tintControl", {"tint": value})
        return self._cast_mapping(result)

    async def picture_size_control(self, size: PictureSize) -> PictureSize:
        result = await self._request("pictureSizeControl", {"pictureSize": size})
        value = self._cast_mapping(result).get("pictureSize")
        if value is None:
            raise SamsungTVProtocolError(
                "pictureSizeControl missing pictureSize in response"
            )
        return self._coerce_enum(value, PictureSize)

    async def sound_mode_control(self, mode: SoundMode) -> SoundMode:
        result = await self._request("soundModeControl", {"soundMode": mode})
        value = self._cast_mapping(result).get("soundMode")
        if value is None:
            raise SamsungTVProtocolError(
                "soundModeControl missing soundMode in response"
            )
        return self._coerce_enum(value, SoundMode)

    async def set_sound_mode(self, mode: SoundMode) -> SoundMode:
        """Convenience alias for sound_mode_control."""

        return await self.sound_mode_control(mode)

    async def speaker_select_control(self, selection: SpeakerSelect) -> SpeakerSelect:
        result = await self._request(
            "speakerSelectControl", {"speakerSelect": selection}
        )
        value = self._cast_mapping(result).get("speakerSelect")
        if value is None:
            raise SamsungTVProtocolError(
                "speakerSelectControl missing speakerSelect in response"
            )
        return self._coerce_enum(value, SpeakerSelect)

    async def select_speaker(self, selection: SpeakerSelect) -> SpeakerSelect:
        """Convenience alias for speaker_select_control."""

        return await self.speaker_select_control(selection)

    async def set_picture_mode(self, mode: PictureMode) -> PictureMode:
        """Convenience alias for picture_mode_control."""

        return await self.picture_mode_control(mode)

    async def set_volume(self, volume: int) -> int:
        """Convenience alias for direct_volume_control."""

        return await self.direct_volume_control(volume)

    async def mute(self) -> MuteState:
        """Enable mute."""

        return await self.mute_control(MuteState.MUTE_ON)

    async def unmute(self) -> MuteState:
        """Disable mute."""

        return await self.mute_control(MuteState.MUTE_OFF)

    async def select_input_source(self, source: InputSource) -> InputSource:
        """Convenience alias for input_source_control."""

        return await self.input_source_control(source)

    async def send_request(
        self,
        method: str,
        params: Mapping[str, Any] | None = None,
        *,
        include_token: bool = True,
    ) -> JSONValue:
        return await self._request(method, params, include_token=include_token)

    async def _request(
        self,
        method: str,
        params: Mapping[str, Any] | None = None,
        *,
        include_token: bool = True,
    ) -> JSONValue:
        payload: dict[str, Any] = {
            "jsonrpc": JSONRPC_VERSION,
            "method": method,
            "id": self._next_request_id(),
        }
        if include_token:
            if not self._access_token:
                raise SamsungTVAuthenticationError("Access token required but not set")
            merged: dict[str, Any] = {"AccessToken": self._access_token}
            if params:
                merged.update(dict(params))
            payload["params"] = merged
        elif params:
            payload["params"] = dict(params)
        data = await self._connection.request(payload)
        if isinstance(data, Mapping) and "error" in data:
            raise SamsungTVResponseError(str(data["error"]))
        if isinstance(data, Mapping):
            result = cast(JSONValue, data.get("result"))
        else:
            result = cast(JSONValue, data)
        await self._notify_update(method, result)
        return result

    async def _notify_update(self, method: str, payload: JSONValue) -> None:
        callback = self._on_update
        if callback is None:
            return
        maybe = callback(method, payload)
        if inspect.isawaitable(maybe):
            await maybe

    def _next_request_id(self) -> int:
        self._request_id += 1
        return self._request_id

    @staticmethod
    def _cast_mapping(value: JSONValue) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise SamsungTVProtocolError("Expected mapping result from TV")
        return value

    @staticmethod
    def _cast_device_list(value: JSONValue) -> list[DeviceInfo]:
        if isinstance(value, Mapping):
            if not value:
                return []
            raise SamsungTVProtocolError("Device entry payload was a mapping")
        if not isinstance(value, Sequence) or isinstance(
            value, (str, bytes, bytearray)
        ):
            raise SamsungTVProtocolError("Expected sequence result from TV")
        devices: list[DeviceInfo] = []
        for entry in value:
            if not isinstance(entry, Mapping):
                raise SamsungTVProtocolError("Device entry was not a mapping")
            device_id = str(entry.get("deviceId"))
            device_name = str(entry.get("deviceName"))
            devices.append(
                cast(DeviceInfo, {"deviceId": device_id, "deviceName": device_name})
            )
        return devices

    @staticmethod
    def _assign_enum_field(
        target: MutableMapping[str, Any],
        source: Mapping[str, Any],
        key: str,
        enum_cls: type[EnumT],
    ) -> None:
        if key not in source:
            return
        target[key] = SamsungTVClient._coerce_enum(source[key], enum_cls)

    @staticmethod
    def _assign_str_field(
        target: MutableMapping[str, Any],
        source: Mapping[str, Any],
        key: str,
    ) -> None:
        if key not in source:
            return
        value = source[key]
        if value is None:
            return
        target[key] = str(value)

    @staticmethod
    def _assign_int_field(
        target: MutableMapping[str, Any],
        source: Mapping[str, Any],
        key: str,
    ) -> None:
        if key not in source:
            return
        value = source[key]
        if value is None:
            return
        try:
            target[key] = int(value)
        except (TypeError, ValueError) as exc:
            raise SamsungTVProtocolError(
                f"Field {key} was not an integer: {value!r}"
            ) from exc

    @staticmethod
    def _coerce_enum(value: Any, enum_cls: type[EnumT]) -> EnumT:
        if isinstance(value, enum_cls):
            return value
        text = str(value)
        try:
            return enum_cls(text)
        except ValueError:
            lowered = text.lower()
            for member in enum_cls:
                if isinstance(member.value, str) and member.value.lower() == lowered:
                    return member
            raise SamsungTVProtocolError(
                f"Unexpected value for {enum_cls.__name__}: {value!r}"
            )


__all__ = ["SamsungTVClient"]

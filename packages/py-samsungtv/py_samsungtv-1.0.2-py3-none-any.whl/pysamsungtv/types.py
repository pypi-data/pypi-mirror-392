"""Shared type aliases and TypedDict definitions."""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Mapping, Sequence, TypedDict, Union

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

JSONPrimitive = Union[str, int, float, bool, None]
JSONValue = Union[JSONPrimitive, Mapping[str, Any], Sequence[Any]]
UpdateCallback = Callable[[str, JSONValue], Awaitable[None] | None]
DirectAccessApp = Union[ApplicationName, str]


class DeviceInfo(TypedDict):
    deviceId: str
    deviceName: str


class TVStates(TypedDict, total=False):
    power: PowerState
    mute: MuteState
    atvDtv: AtvDtv
    airCable: AirCable
    channelNum: str
    inputSource: InputSource
    pictureMode: PictureMode
    artMode: ArtMode


class VideoStates(TypedDict, total=False):
    volume: int
    contrast: int
    brightness: int
    sharpness: int
    color: int
    tint: int
    pictureSize: PictureSize
    soundMode: SoundMode
    speakerSelect: SpeakerSelect


__all__ = [
    "JSONPrimitive",
    "JSONValue",
    "UpdateCallback",
    "DirectAccessApp",
    "DeviceInfo",
    "TVStates",
    "VideoStates",
]

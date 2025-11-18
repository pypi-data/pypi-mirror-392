"""Enumerations for Samsung TV JSON-RPC parameters."""
from __future__ import annotations

from enum import StrEnum


class PowerState(StrEnum):
    """Power control values."""

    POWER_OFF = "powerOff"
    POWER_ON = "powerOn"
    REBOOT = "reboot"


class MuteState(StrEnum):
    """Mute control values."""

    MUTE_OFF = "muteOff"
    MUTE_ON = "muteOn"


class AtvDtv(StrEnum):
    """Analog/digital tuner selector."""

    ATV = "atv"
    DTV = "dtv"


class AirCable(StrEnum):
    """Air/cable selector."""

    AIR = "air"
    CABLE = "cable"


class InputSource(StrEnum):
    """Available input sources."""

    TV = "TV"
    HDMI1 = "HDMI1"
    HDMI2 = "HDMI2"
    HDMI3 = "HDMI3"
    HDMI4 = "HDMI4"
    AV1 = "AV1"
    COMPONENT1 = "COMPONENT1"
    USB = "USB"
    RVU = "RVU"


class PictureMode(StrEnum):
    """Picture mode presets."""

    DYNAMIC = "Dynamic"
    STANDARD = "Standard"
    MOVIE = "Movie"
    NATURAL = "Natural"
    HDR_PLUS = "HDR+"
    FILMMAKER = "FilmmakerMode"


class PictureSize(StrEnum):
    """Picture size options."""

    SIXTEEN_NINE = "16:9"
    FOUR_THREE = "4:3"


class SoundMode(StrEnum):
    """Sound profile options."""

    STANDARD = "Standard"
    AMPLIFY = "Amplify"
    OPTIMIZED = "Optimized"
    EXTERNAL_STANDARD = "ExternalStandard"


class SpeakerSelect(StrEnum):
    """Speaker routing options."""

    INTERNAL = "Internal"
    EXTERNAL = "External"
    AUDIO_OUT_OPTICAL = "AudioOut/Optical"


class ArtMode(StrEnum):
    """Frame TV art mode selector."""

    ART_MODE_OFF = "artModeOff"
    ART_MODE_ON = "artModeOn"


class VolumeAdjust(StrEnum):
    """Volume increment commands."""

    VOLUME_UP = "volumeUp"
    VOLUME_DN = "volumeDn"


class ChannelAdjust(StrEnum):
    """Channel increment commands."""

    CHANNEL_UP = "channelUp"
    CHANNEL_DN = "channelDn"


class RemoteKey(StrEnum):
    """Remote key codes accepted by remoteKeyControl."""

    POWER = "power"
    CURSOR_UP = "cursorUp"
    CURSOR_DN = "cursorDn"
    CURSOR_LEFT = "cursorLeft"
    CURSOR_RIGHT = "cursorRight"
    MENU = "menu"
    FIRST_SCREEN = "firstScreen"
    ENTER = "enter"
    FAST_FORWARD = "fastforward"
    REWIND = "rewind"
    PLAY = "play"
    STOP = "stop"
    PAUSE = "pause"
    RETURN = "return"
    EXIT = "exit"
    NUMBER_0 = "number0"
    NUMBER_1 = "number1"
    NUMBER_2 = "number2"
    NUMBER_3 = "number3"
    NUMBER_4 = "number4"
    NUMBER_5 = "number5"
    NUMBER_6 = "number6"
    NUMBER_7 = "number7"
    NUMBER_8 = "number8"
    NUMBER_9 = "number9"
    CAPTION = "caption"
    DASH = "dash"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    AMBIENT = "ambient"


class ApplicationName(StrEnum):
    """Known direct access application identifiers."""

    WEB_BROWSER = "webBrowser"
    NETFLIX = "netflix"
    AMAZON = "amazon"
    PANDORA = "pandora"
    VUDU = "vudu"
    YOUTUBE = "youTube"
    HULU = "hulu"


__all__ = [
    "PowerState",
    "MuteState",
    "AtvDtv",
    "AirCable",
    "InputSource",
    "PictureMode",
    "PictureSize",
    "SoundMode",
    "SpeakerSelect",
    "ArtMode",
    "VolumeAdjust",
    "ChannelAdjust",
    "RemoteKey",
    "ApplicationName",
]

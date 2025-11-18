"""Data models for Pulse8 Matrix API responses."""

from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class Revision:
    """Board revision information."""
    main: int
    top: int
    ir: int


@dataclass
class SystemDetails:
    """System details response."""
    result: bool
    model: str
    version: str
    serial: str
    mac: str
    vid: str
    board_rev: int
    revision: Revision
    locale: str
    status_message: str
    status: int

    @classmethod
    def from_dict(cls, data: dict) -> "SystemDetails":
        """Create SystemDetails from API response."""
        return cls(
            result=data["Result"],
            model=data["Model"],
            version=data["Version"],
            serial=data["Serial"],
            mac=data["MAC"],
            vid=data["VID"],
            board_rev=data["BoardRev"],
            revision=Revision(**data["revision"]),
            locale=data["Locale"],
            status_message=data["StatusMessage"],
            status=data["Status"],
        )


@dataclass
class VideoFeatures:
    """Video feature information."""
    scrambling: bool
    ir: dict
    input: dict
    output: dict


@dataclass
class AudioFeatures:
    """Audio feature information."""
    arc: dict
    routing: bool
    dsp: bool
    input: dict
    output: dict


@dataclass
class SystemFeatures:
    """System features response."""
    result: bool
    upd_interval: int
    cec: bool
    cec_switching: bool
    cec_logging: int
    cec_usage: int
    pdu: bool
    sky: bool
    hdbaset: bool
    hdbt_upgrade: bool
    mx_remote: bool
    video: VideoFeatures
    audio: AudioFeatures
    backlight_led: str
    status_led: str

    @classmethod
    def from_dict(cls, data: dict) -> "SystemFeatures":
        """Create SystemFeatures from API response."""
        return cls(
            result=data["Result"],
            upd_interval=data["UpdInterval"],
            cec=data["CEC"],
            cec_switching=data["CEC_Switching"],
            cec_logging=data["CEC_Logging"],
            cec_usage=data["CEC_Usage"],
            pdu=data["PDU"],
            sky=data["Sky"],
            hdbaset=data["HDBaseT"],
            hdbt_upgrade=data["hdbt_upgrade"],
            mx_remote=data["mx_remote"],
            video=VideoFeatures(
                scrambling=data["Video"]["Scrambling"],
                ir=data["Video"]["IR"],
                input=data["Video"]["Input"],
                output=data["Video"]["Output"],
            ),
            audio=AudioFeatures(
                arc=data["Audio"]["ARC"],
                routing=data["Audio"]["Routing"],
                dsp=data["Audio"]["DSP"],
                input=data["Audio"]["Input"],
                output=data["Audio"]["Output"],
            ),
            backlight_led=data["BacklightLED"],
            status_led=data["StatusLED"],
        )


@dataclass
class Port:
    """Port information."""
    bay: int
    mode: str  # "Input" or "Output"
    type: str
    status: int
    name: str
    receive_from: Optional[int] = None
    rc_type: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Port":
        """Create Port from API response."""
        return cls(
            bay=data["Bay"],
            mode=data["Mode"],
            type=data["Type"],
            status=data["Status"],
            name=data["Name"],
            receive_from=data.get("ReceiveFrom"),
            rc_type=data.get("rcType"),
        )


@dataclass
class PortListResponse:
    """Port list response."""
    result: bool
    ports: List[Port]

    @classmethod
    def from_dict(cls, data: dict) -> "PortListResponse":
        """Create PortListResponse from API response."""
        return cls(
            result=data["Result"],
            ports=[Port.from_dict(p) for p in data["Ports"]],
        )


@dataclass
class PortDetails:
    """Detailed port information."""
    result: bool
    bay: int
    mode: str
    type: str
    status: int
    name: str
    status_message: str
    transmission_nodes: List[Any]
    hdcp: Optional[int] = None
    hpd: Optional[int] = None
    has_signal: Optional[bool] = None
    signal: Optional[str] = None
    remote: Optional[int] = None
    remote_status: Optional[str] = None
    remote_online: Optional[int] = None
    config_remote: Optional[int] = None
    allowed_sinks: Optional[List[int]] = None
    edid_profile: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PortDetails":
        """Create PortDetails from API response."""
        return cls(
            result=data["Result"],
            bay=data["Bay"],
            mode=data["Mode"],
            type=data["Type"],
            status=data["Status"],
            name=data["Name"],
            status_message=data["StatusMessage"],
            transmission_nodes=data["TransmissionNodes"],
            hdcp=data.get("HDCP"),
            hpd=data.get("HPD"),
            has_signal=data.get("HasSignal"),
            signal=data.get("Signal"),
            remote=data.get("Remote"),
            remote_status=data.get("RemoteStatus"),
            remote_online=data.get("RemoteOnline"),
            config_remote=data.get("ConfigRemote"),
            allowed_sinks=data.get("AllowedSinks"),
            edid_profile=data.get("EdidProfile"),
        )


@dataclass
class SetPortResponse:
    """Response from setting a port connection."""
    result: bool
    message: str

    @classmethod
    def from_dict(cls, data: dict) -> "SetPortResponse":
        """Create SetPortResponse from API response."""
        return cls(
            result=data["Result"],
            message=data["Message"],
        )
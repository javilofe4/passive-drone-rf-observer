from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, Type
import os


def _env_flag(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).lower() in ("1", "true", "yes")


class RadioHardwareProfile(ABC):
    name: str
    description: str
    supports_rx_only: bool
    enable_sdr: bool
    enable_wifi_monitor: bool
    enable_hackrf: bool

    @property
    @abstractmethod
    def profile_key(self) -> str:
        ...

    @classmethod
    @abstractmethod
    def default(cls) -> "RadioHardwareProfile":
        ...


@dataclass
class SimulatedProfile(RadioHardwareProfile):
    name: str = "simulated"
    description: str = "Simulación local sin hardware SDR obligatorio."
    supports_rx_only: bool = True
    enable_sdr: bool = False
    enable_wifi_monitor: bool = False
    enable_hackrf: bool = False

    @property
    def profile_key(self) -> str:
        return self.name

    @classmethod
    def default(cls) -> "SimulatedProfile":
        return cls()


@dataclass
class WifiBleRemoteIDProfile(RadioHardwareProfile):
    name: str = "wifi_ble_remote_id"
    description: str = "Perfil básico para Wi-Fi monitor mode y Bluetooth/BLE local."
    supports_rx_only: bool = True
    enable_sdr: bool = False
    enable_wifi_monitor: bool = True
    enable_hackrf: bool = False

    @property
    def profile_key(self) -> str:
        return self.name

    @classmethod
    def default(cls) -> "WifiBleRemoteIDProfile":
        return cls()


@dataclass
class RTLSDRv4Profile(RadioHardwareProfile):
    name: str = "rtl_sdr_v4"
    description: str = "Perfil SDR básico con RTL-SDR Blog V4 para recepción pasiva sub-GHz."
    supports_rx_only: bool = True
    enable_sdr: bool = True
    enable_wifi_monitor: bool = False
    enable_hackrf: bool = False

    @property
    def profile_key(self) -> str:
        return self.name

    @classmethod
    def default(cls) -> "RTLSDRv4Profile":
        return cls()


@dataclass
class HackRFRxOnlyProfile(RadioHardwareProfile):
    name: str = "hackrf_rx_only"
    description: str = "Perfil SDR avanzado para HackRF en modo RX-only entre 1 MHz y 6 GHz."
    supports_rx_only: bool = True
    enable_sdr: bool = True
    enable_wifi_monitor: bool = False
    enable_hackrf: bool = True

    @property
    def profile_key(self) -> str:
        return self.name

    @classmethod
    def default(cls) -> "HackRFRxOnlyProfile":
        return cls()


PROFILE_CLASSES: ClassVar[Dict[str, Type[RadioHardwareProfile]]] = {
    "simulated": SimulatedProfile,
    "wifi_ble_remote_id": WifiBleRemoteIDProfile,
    "rtl_sdr_v4": RTLSDRv4Profile,
    "hackrf_rx_only": HackRFRxOnlyProfile,
}


def get_radio_hardware_profile(profile_name: str) -> RadioHardwareProfile:
    profile_cls = PROFILE_CLASSES.get(profile_name, SimulatedProfile)
    return profile_cls.default()


def default_hardware_profile() -> RadioHardwareProfile:
    name = __import__("os").getenv("PDRFO_HARDWARE_PROFILE", "simulated")
    return get_radio_hardware_profile(name)

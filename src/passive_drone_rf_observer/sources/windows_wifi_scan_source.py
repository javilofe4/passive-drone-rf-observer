from __future__ import annotations
import hashlib
import platform
import subprocess
import time
from typing import Dict, List, Optional

from ..models import SourceType, WifiObservation


class WindowsWifiScanSource:
    def __init__(self, salt: str = "local-dev-salt"):
        self.salt = salt

    def scan(self) -> List[WifiObservation]:
        output = self._run_netsh()
        if not output:
            return []
        raw_observations = self._parse_netsh_output(output)
        return [self._normalize_observation(raw) for raw in raw_observations]

    def _run_netsh(self) -> Optional[str]:
        if platform.system().lower() != "windows":
            return None

        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
        except (subprocess.SubprocessError, OSError):
            return None

        if result.returncode != 0 or not result.stdout:
            return None

        return result.stdout

    def _parse_netsh_output(self, output: str) -> List[Dict[str, Optional[str]]]:
        observations: List[Dict[str, Optional[str]]] = []
        current_ssid: Optional[str] = None
        current_bssid: Optional[str] = None
        current_signal: Optional[int] = None
        current_channel: Optional[int] = None
        current_radio_type: Optional[str] = None
        current_auth: Optional[str] = None

        def flush_bssid() -> None:
            nonlocal current_bssid, current_signal, current_channel, current_radio_type, current_auth
            if current_ssid is None or current_bssid is None:
                return
            observations.append(
                {
                    "ssid": current_ssid,
                    "bssid": current_bssid,
                    "signal_percent": current_signal,
                    "channel": current_channel,
                    "radio_type": current_radio_type,
                    "authentication": current_auth,
                }
            )
            current_bssid = None
            current_signal = None
            current_channel = None
            current_radio_type = None
            current_auth = None

        for raw_line in output.splitlines():
            line = raw_line.strip()
            if line.startswith("SSID ") and " : " in line:
                flush_bssid()
                current_ssid = line.split(" : ", 1)[1].strip()
                continue
            if line.lower().startswith("bssid") and " : " in line:
                flush_bssid()
                current_bssid = line.split(" : ", 1)[1].strip()
                continue
            if line.lower().startswith("signal") and " : " in line:
                value = line.split(" : ", 1)[1].strip().rstrip("%")
                try:
                    current_signal = int(value)
                except ValueError:
                    current_signal = None
                continue
            if line.lower().startswith("channel") and " : " in line:
                value = line.split(" : ", 1)[1].strip()
                try:
                    current_channel = int(value)
                except ValueError:
                    current_channel = None
                continue
            if line.lower().startswith("radio type") and " : " in line:
                current_radio_type = line.split(" : ", 1)[1].strip()
                continue
            if line.lower().startswith("authentication") and " : " in line:
                current_auth = line.split(" : ", 1)[1].strip()
                continue

        flush_bssid()
        return observations

    def _hash_bssid(self, bssid: str) -> str:
        return hashlib.sha256((bssid.lower() + self.salt).encode("utf-8")).hexdigest()

    def _normalize_observation(self, raw: Dict[str, Optional[str]]) -> WifiObservation:
        return WifiObservation(
            timestamp=time.time(),
            ssid=raw.get("ssid", ""),
            bssid_hash=self._hash_bssid(raw.get("bssid", "")),
            signal_percent=raw.get("signal_percent") or 0,
            channel=raw.get("channel"),
            radio_type=raw.get("radio_type"),
            authentication=raw.get("authentication"),
            source=SourceType.WINDOWS_WIFI_SCAN,
        )

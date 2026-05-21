from __future__ import annotations
import hashlib
import platform
import subprocess
from typing import List, Optional

from ..models import WifiObservation


class WindowsWifiScanSource:
    def __init__(self, salt: str = "local-dev-salt"):
        self.salt = salt

    def scan(self) -> List[WifiObservation]:
        if platform.system().lower() != "windows":
            return []

        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
        except (subprocess.SubprocessError, OSError):
            return []

        if result.returncode != 0 or not result.stdout:
            return []

        return self._parse_netsh_output(result.stdout)

    def _parse_netsh_output(self, output: str) -> List[WifiObservation]:
        observations: List[WifiObservation] = []
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
            bssid_hash = hashlib.sha256((current_bssid.lower() + self.salt).encode("utf-8")).hexdigest()
            observations.append(
                WifiObservation(
                    timestamp=__import__("time").time(),
                    ssid=current_ssid,
                    bssid_hash=bssid_hash,
                    signal_percent=current_signal or 0,
                    channel=current_channel,
                    radio_type=current_radio_type,
                    authentication=current_auth,
                )
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

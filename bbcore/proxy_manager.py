"""
Proxy rotation engine.
Supports: Tor SOCKS5, BrightData, Webshare, file-based proxy lists.
"""
import os
import random
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Proxy:
    protocol: str  # http, https, socks5, socks4
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None

    @property
    def url(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.protocol}://{auth}{self.host}:{self.port}"

    @property
    def curl_flag(self) -> str:
        if self.protocol.startswith("socks"):
            return f"--socks5 {self.host}:{self.port}"
        return f"-x {self.url}"


class ProxyManager:
    """Manages proxy rotation for recon tools."""

    MODE_DIRECT = "direct"
    MODE_TOR = "tor"
    MODE_STATIC = "static"
    MODE_ROTATE = "rotate"

    def __init__(self, config_path: Optional[Path] = None):
        self.mode = self.MODE_DIRECT
        self.static_proxy: Optional[Proxy] = None
        self.proxy_list: list[Proxy] = []
        self._current_index = 0
        self._lock = threading.Lock()
        self.config_path = None
        env_config = os.environ.get("BB_CONFIG", "")
        if env_config:
            self.config_path = Path(env_config)
        if config_path:
            self.config_path = config_path
        self._tor_process: Optional[subprocess.Popen] = None
        self.load_config()

    def load_config(self):
        """Load proxy config from environment or config file."""
        if self.config_path and self.config_path.is_file() and self.config_path.exists():
            lines = self.config_path.read_text().splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("PROXY_MODE="):
                    self.mode = line.split("=", 1)[1]
                elif line.startswith("PROXY_STATIC="):
                    parts = line.split("=", 1)[1]
                    self.static_proxy = self._parse_proxy(parts)
                elif line.startswith("PROXY_FILE="):
                    proxy_file = Path(line.split("=", 1)[1])
                    if proxy_file.exists():
                        for pline in proxy_file.read_text().splitlines():
                            pline = pline.strip()
                            if pline and not pline.startswith("#"):
                                p = self._parse_proxy(pline)
                                if p:
                                    self.proxy_list.append(p)

        # Fall back to env vars
        env_mode = os.environ.get("BB_PROXY_MODE", "")
        if env_mode:
            self.mode = env_mode
        env_static = os.environ.get("BB_PROXY_STATIC", "")
        if env_static:
            self.static_proxy = self._parse_proxy(env_static)

    def _parse_proxy(self, text: str) -> Optional[Proxy]:
        """Parse proxy from string: protocol://user:pass@host:port"""
        try:
            if "://" not in text:
                text = f"http://{text}"
            proto, rest = text.split("://", 1)
            proto = proto.lower()
            if "@" in rest:
                auth, hostport = rest.rsplit("@", 1)
                user, pw = auth.split(":", 1) if ":" in auth else (auth, "")
            else:
                user, pw, hostport = None, None, rest
            host, port_str = hostport.rsplit(":", 1)
            return Proxy(proto, host, int(port_str), user, pw)
        except Exception:
            return None

    @property
    def current(self) -> Optional[Proxy]:
        if self.mode == self.MODE_DIRECT:
            return None
        if self.mode == self.MODE_TOR:
            return Proxy("socks5", "127.0.0.1", 9050)
        if self.mode == self.MODE_STATIC:
            return self.static_proxy
        if self.mode == self.MODE_ROTATE:
            with self._lock:
                if not self.proxy_list:
                    return None
                proxy = self.proxy_list[self._current_index % len(self.proxy_list)]
                self._current_index += 1
                return proxy
        return None

    def get_env(self) -> dict[str, str]:
        """Get environment variables for child processes."""
        proxy = self.current
        if proxy is None:
            return {}
        return {
            "HTTP_PROXY": proxy.url,
            "HTTPS_PROXY": proxy.url,
            "ALL_PROXY": proxy.url,
            "NO_PROXY": "127.0.0.1,localhost,.local",
        }

    def curl_args(self) -> list[str]:
        proxy = self.current
        if proxy is None:
            return []
        if proxy.protocol.startswith("socks"):
            return ["--socks5", f"{proxy.host}:{proxy.port}"]
        return ["-x", proxy.url]

    def start_tor(self, tor_path: Optional[str] = None) -> bool:
        """Start Tor process if not running."""
        if self._tor_process and self._tor_process.poll() is None:
            return True
        paths = [
            tor_path,
            str(Path.cwd() / "tor_bundle" / "Tor" / "tor.exe"),
            str(Path.home() / "scoop" / "apps" / "tor" / "current" / "tor.exe"),
            "tor",
        ]
        for p in paths:
            if p and Path(p).exists():
                try:
                    self._tor_process = subprocess.Popen(
                        [p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    time.sleep(3)
                    self.mode = self.MODE_TOR
                    return True
                except Exception:
                    continue
        return False

    def stop_tor(self):
        if self._tor_process:
            self._tor_process.kill()
            self._tor_process = None

    def rotate(self) -> Optional[Proxy]:
        """Force rotate to next proxy."""
        if self.mode != self.MODE_ROTATE or not self.proxy_list:
            return self.current
        with self._lock:
            self._current_index += 1
            p = self.proxy_list[self._current_index % len(self.proxy_list)]
            return p

    def status_text(self) -> str:
        if self.mode == self.MODE_DIRECT:
            return "Direct"
        if self.mode == self.MODE_TOR:
            return "Tor"
        p = self.current
        if p:
            return f"{p.protocol.upper()} {p.host}:{p.port}"
        return "None"

import os
import sys
import platform
import stat
from pathlib import Path
from typing import Optional, Dict
import httpx
from loguru import logger
from .auth import GitHubTokenStorage


class BinaryInstaller:
    GITHUB_REPO = "nexroo-ai/nexroo-engine"
    BINARY_DIR = Path.home() / ".nexroo" / "bin"

    def __init__(self):
        self.platform = self._detect_platform()
        self.binary_name = "nexroo-engine.exe" if self.platform == "windows" else "nexroo-engine"
        self.binary_path = self.BINARY_DIR / self.binary_name
        self.github_storage = GitHubTokenStorage()

    def _detect_platform(self) -> str:
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            raise Exception(f"Unsupported platform: {system}")

    def _get_asset_name(self) -> str:
        if self.platform == "linux":
            return "nexroo-engine-linux-amd64"
        elif self.platform == "macos":
            return "nexroo-engine-macos-amd64"
        elif self.platform == "windows":
            return "nexroo-engine-windows-amd64.exe"

    def _get_headers(self) -> Dict[str, str]:
        headers = {}
        token = self.github_storage.get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def get_latest_release_url(self) -> str:
        url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
        headers = self._get_headers()

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                release_data = response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    if not self.github_storage.has_token() and not self.github_storage.DEV_TOKEN:
                        raise Exception(
                            "Access token required to download nexroo-engine.\n"
                            "Please login first."
                        )
                    else:
                        raise Exception(
                            "Repository not found or no releases available.\n"
                            "Verify your access token or check if releases exist."
                        )
                raise

        asset_name = self._get_asset_name()

        for asset in release_data.get("assets", []):
            if asset["name"] == asset_name:
                return asset["browser_download_url"]

        raise Exception(f"Binary not found for platform: {self.platform}")

    async def download_binary(self, url: str) -> Path:
        logger.info(f"Downloading nexroo-engine for {self.platform}...")

        self.BINARY_DIR.mkdir(parents=True, exist_ok=True)
        headers = self._get_headers()

        async with httpx.AsyncClient(follow_redirects=True) as client:
            async with client.stream("GET", url, headers=headers) as response:
                response.raise_for_status()

                total = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(self.binary_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            percent = (downloaded / total) * 100
                            logger.debug(f"Progress: {percent:.1f}%")

        if self.platform != "windows":
            self.binary_path.chmod(self.binary_path.stat().st_mode | stat.S_IEXEC)

        logger.info(f"Engine installed to {self.binary_path}")
        return self.binary_path

    async def install(self) -> Path:
        if self.is_installed():
            logger.info("nexroo-engine already installed")
            return self.binary_path

        try:
            download_url = await self.get_latest_release_url()
            return await self.download_binary(download_url)
        except Exception as e:
            logger.error(f"Failed to install nexroo-engine: {e}")
            raise

    def is_installed(self) -> bool:
        return self.binary_path.exists()

    def get_binary_path(self) -> Optional[Path]:
        if self.is_installed():
            return self.binary_path
        return None

    async def update(self) -> Path:
        logger.info("Checking for updates...")
        download_url = await self.get_latest_release_url()

        if self.binary_path.exists():
            self.binary_path.unlink()

        return await self.download_binary(download_url)

    def uninstall(self):
        if self.binary_path.exists():
            self.binary_path.unlink()
            logger.info("nexroo-engine uninstalled")
        else:
            logger.info("nexroo-engine not found")

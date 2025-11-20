from pathlib import Path
from typing import Optional
from loguru import logger


class GitHubTokenStorage:
    DEV_TOKEN = None

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".nexroo"

        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.token_file = self.storage_dir / "github_token"

    def save_token(self, token: str):
        self.token_file.write_text(token.strip())
        logger.info("Installation access configured successfully")

    def load_token(self) -> Optional[str]:
        if not self.token_file.exists():
            return None

        try:
            return self.token_file.read_text().strip()
        except Exception as e:
            logger.error(f"Unable to verify installation access: {e}")
            return None

    def has_token(self) -> bool:
        return self.token_file.exists()

    def get_token(self) -> Optional[str]:
        if self.DEV_TOKEN:
            return self.DEV_TOKEN
        return self.load_token()

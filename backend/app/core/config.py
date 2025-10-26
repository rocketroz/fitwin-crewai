import os
from dataclasses import dataclass

@dataclass
class Settings:
    env: str = os.getenv("ENV", "dev")
    vendor_mode: str = os.getenv("VENDOR_MODE", "stub")


settings = Settings()

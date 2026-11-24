"""Runtime configuration read once from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str
    use_ssl: bool

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        is_local = os.getenv("IS_LOCAL", "false").lower() == "true"
        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            name=os.getenv("POSTGRES_NAME", "postgres"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASS", ""),
            use_ssl=not is_local,
        )

    def to_conninfo(self) -> str:
        sslmode = "require" if self.use_ssl else "disable"
        return (
            f"host={self.host} port={self.port} dbname={self.name} "
            f"user={self.user} password={self.password} "
            f"sslmode={sslmode} connect_timeout=15"
        )

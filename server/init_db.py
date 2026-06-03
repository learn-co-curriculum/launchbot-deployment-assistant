"""Initialize the SQLite database used for chat threads."""

from app.config import Config
from app.services.thread_service import ensure_database


def main() -> None:
    """Create the SQLite tables if they do not already exist."""
    ensure_database(Config.DATABASE_PATH)
    print(f"Initialized SQLite database at {Config.DATABASE_PATH}")


if __name__ == "__main__":
    main()

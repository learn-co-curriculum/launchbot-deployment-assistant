"""Seed the Chroma vector store with deployment runbook chunks."""

from app.services.vector_store import seed_vector_store


def main() -> None:
    """Seed Chroma and report how many chunks were stored."""
    count = seed_vector_store(reset=True)
    print(f"Seeded {count} deployment runbook chunks into Chroma.")


if __name__ == "__main__":
    main()

from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

__all__ = [
    "TestDatabase",
]


class TestDatabase:
    """The Highlighter agent database

    Each instance creates its own in-memory SQLite database to ensure test isolation.
    """

    def __init__(self):
        # Create a fresh in-memory database for each instance
        # This ensures tests don't interfere with each other
        self.engine: Engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        return Session(self.engine)

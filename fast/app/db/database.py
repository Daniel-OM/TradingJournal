'''
from sqlalchemy import create_engine, Column, Integer, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime

from app.core.config import settings

# Crear engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
)
'''

from datetime import datetime, timezone
import contextlib
from contextvars import ContextVar
from typing import Any, AsyncIterator


from sqlalchemy import ForeignKey, create_engine, Column, Integer, DateTime, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

_session_ctx: ContextVar[AsyncSession] = ContextVar("session")

class DatabaseSessionManager:

    def __init__(self, url: str, engine_kwargs: dict[str, Any] = {}) -> None:
        self._engine: AsyncEngine = create_async_engine(url=url, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine, expire_on_commit=False, autoflush=False)

    async def close(self) -> None:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    def get_session(self) -> AsyncSession:
        return _session_ctx.get()
    
    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session: AsyncSession = self._sessionmaker()
        token = _session_ctx.set(session)
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

echo_db = settings.ENVIRONMENT != 'production'
sessionmanager = DatabaseSessionManager(url=settings.DATABASE_URL, 
                                        engine_kwargs={"echo": echo_db, 'future':True})


# Crear base para modelos
Base = declarative_base()

class BaseModel(Base):
    """
    Abstract base model with common fields for all models
    """
    __abstract__ = True

    id: Column[int] = Column(Integer, primary_key=True, index=True)
    created_at: Column[datetime] = Column(DateTime, default=datetime.now(tz=timezone.utc), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    updated_at: Column[datetime] = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_active: Column[bool] = Column(Boolean, default=True)
    
    
    @property
    def db(self) -> AsyncSession:
        return sessionmanager.get_session()
    
    @staticmethod
    def _currentDateTime() -> datetime:
        return datetime.now(tz=timezone.utc) if 'sqlite' in settings.DATABASE_URL else datetime.now(tz=timezone.utc)
    
    @staticmethod
    def _ensureTimezone(dt: datetime | None) -> datetime | None:
        """Asegura que una fecha tenga timezone"""
        if dt is None:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def __setattr__(self, key, value) -> None:
        """Intercepta asignaciones a columnas DateTime para asegurar timezone"""
        if isinstance(value, datetime):
            value = self._ensureTimezone(dt=value)
        super().__setattr__(key, value)

    async def refresh(self):
        await self.db.refresh(instance=self)
        return self

    async def delete(self, permanent: bool = False) -> bool:
        """Método común para eliminar registros"""
        try:
            if permanent:
                await self.db.delete(instance=self)
            else:
                self.deleted_at: datetime = self._currentDateTime()
                self.active = False
            await self.db.commit()
            return True
        except Exception as e:
            print('Error deleting entity: ', e)
            return False

async def get_db():
    async with sessionmanager.session() as session:
        yield session
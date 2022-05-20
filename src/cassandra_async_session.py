# Credits: https://github.com/CharAct3/aiocqlengine/blob/b2e7932cae37b9826d9458401f0ace460228ee08/aiocqlengine/session.py
import asyncio
import typing as t
from types import MethodType
from functools import partial

from cassandra.cluster import (
    ResponseFuture,
    ResultSet,
    Session,
)
from cassandra.query import PreparedStatement


def _asyncio_result(
    self: Session,
    async_fut: asyncio.Future[t.Any],
    cassandra_fut: ResponseFuture,
    result: t.Any,
) -> None:
    if async_fut.cancelled():
        return

    result_set = ResultSet(cassandra_fut, result)
    self._asyncio_loop.call_soon_threadsafe(async_fut.set_result, result_set)


def _asyncio_exception(
    self: Session, async_fut: asyncio.Future[t.Any], exc: t.Any
) -> None:
    if async_fut.cancelled():
        return

    self._asyncio_loop.call_soon_threadsafe(async_fut.set_exception, exc)


async def execute_asyncio(
    self: Session, statement: str | PreparedStatement, *args: t.Any, **kwargs: t.Any
) -> t.Any:
    fut = self.execute_async(statement, *args, **kwargs)

    future = self._asyncio_loop.create_future()

    fut.add_callbacks(
        callback=partial(self._asyncio_result, future, fut),
        errback=partial(self._asyncio_exception, future),
    )

    return await future


async def prepare_asyncio(
    self: Session, statement: str | PreparedStatement
) -> PreparedStatement:
    return await self._asyncio_loop.run_in_executor(None, self.prepare, statement)


async def set_keyspace_asyncio(self: Session, keyspace: str) -> None:
    await self._asyncio_loop.run_in_executor(None, self.set_keyspace, keyspace)


def load_asyncio_to_session(session: Session) -> Session:
    session._asyncio_loop = asyncio.get_event_loop()
    session._asyncio_exception = MethodType(_asyncio_exception, session)
    session._asyncio_result = MethodType(_asyncio_result, session)
    session.execute_asyncio = MethodType(execute_asyncio, session)
    session.prepare_asyncio = MethodType(prepare_asyncio, session)
    session.set_keyspace_asyncio = MethodType(set_keyspace_asyncio, session)
    return session

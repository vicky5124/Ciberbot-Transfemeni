# Credits: https://github.com/CharAct3/aiocqlengine/blob/b2e7932cae37b9826d9458401f0ace460228ee08/aiocqlengine/session.py
import asyncio
import typing as t
from functools import partial

from cassandra.cluster import (
    ResponseFuture,
    ResultSet,
    Session,
)
from cassandra.query import PreparedStatement


class AsyncioSession(Session): # type: ignore
    def __init__(self, session: Session):
        self.__dict__.update(session.__dict__)
        self._asyncio_loop = asyncio.get_event_loop()
        # stop the garbage collector from making the cluster stop working
        self.session = session

    def _asyncio_result(
        self,
        async_fut: asyncio.Future[t.Any],
        cassandra_fut: ResponseFuture,
        result: t.Any,
    ) -> None:
        if async_fut.done():
            return

        result_set = ResultSet(cassandra_fut, result)
        self._asyncio_loop.call_soon_threadsafe(async_fut.set_result, result_set)

    def _asyncio_exception(self, async_fut: asyncio.Future[t.Any], exc: t.Any) -> None:
        if async_fut.done():
            return

        self._asyncio_loop.call_soon_threadsafe(async_fut.set_exception, exc)

    async def execute_asyncio(
        self, statement: str | PreparedStatement, *args: t.Any, **kwargs: t.Any
    ) -> t.Any:
        fut = self.execute_async(statement, *args, **kwargs)

        future = self._asyncio_loop.create_future()

        fut.add_callbacks(
            callback=partial(self._asyncio_result, future, fut),
            errback=partial(self._asyncio_exception, future),
        )

        return await future

    async def prepare_asyncio(
        self, statement: str | PreparedStatement
    ) -> PreparedStatement:
        return await self._asyncio_loop.run_in_executor(None, self.prepare, statement)

    async def set_keyspace_asyncio(self, keyspace: str) -> None:
        await self._asyncio_loop.run_in_executor(None, self.set_keyspace, keyspace)


def load_asyncio_to_session(session: Session) -> AsyncioSession:
    return AsyncioSession(session)

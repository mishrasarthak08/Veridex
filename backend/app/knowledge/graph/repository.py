from neo4j import AsyncGraphDatabase
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from neo4j.exceptions import ServiceUnavailable, SessionExpired
from app.core.config import settings

class GraphRepository:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))

    async def close(self):
        await self.driver.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ServiceUnavailable, SessionExpired))
    )
    async def execute_query(self, query: str, parameters: dict = None):
        if parameters is None:
            parameters = {}
        async with self.driver.session() as session:
            result = await session.run(query, parameters)
            records = await result.data()
            return records

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ServiceUnavailable, SessionExpired))
    )
    async def execute_write(self, query: str, parameters: dict = None):
        if parameters is None:
            parameters = {}
        async with self.driver.session() as session:
            # For writes, execute_write provides better routing in cluster mode
            # but session.run works for basic cases. We'll use session.run in a transaction
            async def _do_write(tx):
                result = await tx.run(query, parameters)
                return await result.data()
                
            return await session.execute_write(_do_write)

from abc import ABC


class PostgresDBRepositoryInterface(ABC):
    def get_postgres_db_repository(self):
        pass
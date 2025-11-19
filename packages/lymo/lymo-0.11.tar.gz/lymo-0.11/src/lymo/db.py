from typing import TypeVar, Generic, List, Optional, Any, Dict, Type, ClassVar, Tuple, Literal
from datetime import datetime, date as date_type
from pydantic import BaseModel, ConfigDict
from psycopg.rows import dict_row
import inspect
import re


T = TypeVar("T", bound="Model")


class Manager(Generic[T]):
    """
    Django-style manager for database queries with chainable methods.
    """

    def __init__(self, model_class: Type[T], conn: Any):
        self.model_class = model_class
        self.conn = conn
        self._filters: Dict[str, Any] = {}
        self._date_ranges: List[Tuple[str, Any, Any]] = []
        self._date_between_filters: List[Tuple[str, Any, Any]] = []
        self._date_filters: List[Tuple[str, date_type]] = []
        self._between_filters: List[Tuple[str, Any, Any]] = []
        self._limit_value: Optional[int] = None
        self._offset_value: int = 0
        self._order_by_value: Optional[str] = None

    def _clone(self) -> "Manager[T]":
        new_manager = Manager(self.model_class, self.conn)
        new_manager._filters = self._filters.copy()
        new_manager._date_ranges = self._date_ranges.copy()
        new_manager._date_between_filters = self._date_between_filters.copy()
        new_manager._date_filters = self._date_filters.copy()
        new_manager._between_filters = self._between_filters.copy()
        new_manager._limit_value = self._limit_value
        new_manager._offset_value = self._offset_value
        new_manager._order_by_value = self._order_by_value
        return new_manager

    def find(self, **filters) -> "Manager[T]":
        """
        Add WHERE filters to the query. Chainable.

        Args:
            **filters: Column name and value pairs to filter by

        Returns:
            New Manager instance with filters applied
        """
        new_manager = self._clone()
        new_manager._filters.update(filters)
        return new_manager

    def limit(self, limit: int, offset: int = 0) -> "Manager[T]":
        """
        Set LIMIT and OFFSET for the query. Chainable.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip (default: 0)

        Returns:
            New Manager instance with limit/offset applied
        """
        new_manager = self._clone()
        new_manager._limit_value = limit
        new_manager._offset_value = offset
        return new_manager

    def paginate(self, page: int = 1, per_page: int = 50) -> "Manager[T]":
        """
        Apply pagination to the query. Chainable.

        Args:
            page: Page number (1-indexed, default: 1)
            per_page: Items per page (default: 50)

        Returns:
            New Manager instance with pagination applied

        Example:
            # Get page 1 (first 50 records)
            Post.objects.using(conn).order_by('created_at', 'DESC').paginate(page=1).list()

            # Get page 2 with 100 items per page
            Post.objects.using(conn).paginate(page=2, per_page=100).list()
        """
        offset = (page - 1) * per_page
        return self.limit(per_page, offset)

    def order_by(self, column: str, direction: Literal["ASC", "DESC"] = "ASC") -> "Manager[T]":
        """
        Set ORDER BY clause for the query. Chainable.

        Args:
            column: Column name to order by (e.g., 'created_at', 'updated_at')
            direction: Sort direction - 'ASC' or 'DESC' (default: 'ASC')

        Returns:
            New Manager instance with ordering applied

        Example:
            # Ascending (default)
            Post.objects.using(conn).order_by('created_at').list()

            # Descending
            Post.objects.using(conn).order_by('created_at', 'DESC').list()
        """
        new_manager = self._clone()
        new_manager._order_by_value = f"{column} {direction}"
        return new_manager

    def date_range(
        self,
        column: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> "Manager[T]":
        """
        Add an inclusive date range filter using BETWEEN (includes end date). Chainable.

        Args:
            column: Column name to filter (e.g., 'created_at', 'updated_at')
            date_from: Start date inclusive (default: datetime.min - beginning of time)
            date_to: End date inclusive (default: datetime.max - end of time)

        Returns:
            New Manager instance with date range applied

        Example:
            # Inclusive range - includes records from Jan 1 through Dec 31
            Post.objects.using(conn).date_range('created_at',
                date_from=datetime(2024, 1, 1),
                date_to=datetime(2024, 12, 31)
            ).list()
            # SQL: WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'

            # From date onwards
            Post.objects.using(conn).date_range('created_at',
                date_from=datetime(2024, 6, 15)
            ).list()
        """
        new_manager = self._clone()

        if date_from is None:
            date_from = datetime.min
        if date_to is None:
            date_to = datetime.max

        new_manager._date_ranges.append((column, date_from, date_to))
        return new_manager

    def date_between(
        self,
        column: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> "Manager[T]":
        """
        Add an exclusive date range filter (excludes end date). Chainable.

        Args:
            column: Column name to filter (e.g., 'created_at', 'updated_at')
            date_from: Start date inclusive (default: datetime.min - beginning of time)
            date_to: End date exclusive - not included (default: datetime.max - end of time)

        Returns:
            New Manager instance with date between filter applied

        Example:
            # Exclusive range - includes Jan 1 up to but NOT including Jan 31
            Post.objects.using(conn).date_between('created_at',
                date_from=datetime(2024, 1, 1),
                date_to=datetime(2024, 1, 31)
            ).list()
            # SQL: WHERE created_at >= '2024-01-01' AND created_at < '2024-01-31'

            # All records before a date (exclusive)
            Post.objects.using(conn).date_between('created_at',
                date_to=datetime(2024, 6, 15)
            ).list()
        """
        new_manager = self._clone()

        if date_from is None:
            date_from = datetime.min
        if date_to is None:
            date_to = datetime.max

        new_manager._date_between_filters.append((column, date_from, date_to))
        return new_manager

    def date(
        self,
        column: str,
        target_date: datetime | date_type
    ) -> "Manager[T]":
        """
        Filter for records on a specific date only (time is stripped). Chainable.

        Args:
            column: Column name to filter (e.g., 'created_at', 'updated_at')
            target_date: Date to match (datetime or date object - time is stripped)

        Returns:
            New Manager instance with date filter applied

        Example:
            # Using date object
            from datetime import date
            Post.objects.using(conn).date('created_at', date(2024, 1, 15)).list()

            # Using datetime (time is stripped)
            Post.objects.using(conn).date('created_at', datetime(2024, 1, 15, 14, 30)).list()

            # SQL: WHERE DATE(created_at) = '2024-01-15'
        """
        new_manager = self._clone()

        if isinstance(target_date, datetime):
            target_date = target_date.date()

        new_manager._date_filters.append((column, target_date))
        return new_manager

    def between(self, column: str, value_from: Any, value_to: Any) -> "Manager[T]":
        """
        Add a BETWEEN filter for any column type. Chainable.

        Args:
            column: Column name to filter
            value_from: Start value (inclusive)
            value_to: End value (inclusive)

        Returns:
            New Manager instance with between filter applied

        Example:
            # Numeric range
            Product.objects.using(conn).between('price', 100, 500).list()

            # String range
            Product.objects.using(conn).between('sku', 'A', 'M').list()

            # UUID range
            Order.objects.using(conn).between('order_id', uuid1, uuid2).list()
        """
        new_manager = self._clone()
        new_manager._between_filters.append((column, value_from, value_to))
        return new_manager

    @staticmethod
    def _get_table_name(model_class: Type[T]) -> str:
        name = model_class.__name__
        snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return snake_case

    def _is_async_connection(self) -> bool:
        return inspect.iscoroutinefunction(
            getattr(self.conn, "execute", None)
        ) or hasattr(self.conn, "__aenter__")

    def _build_where_clause(self) -> tuple[str, list]:
        where_clauses = []
        params = []

        if self._filters:
            for key, value in self._filters.items():
                where_clauses.append(f"{key} = %s")
                params.append(value)

        if self._date_ranges:
            for column, date_from, date_to in self._date_ranges:
                where_clauses.append(f"{column} BETWEEN %s AND %s")
                params.append(date_from)
                params.append(date_to)

        if self._date_between_filters:
            for column, date_from, date_to in self._date_between_filters:
                where_clauses.append(f"{column} >= %s AND {column} < %s")
                params.append(date_from)
                params.append(date_to)

        if self._date_filters:
            for column, target_date in self._date_filters:
                where_clauses.append(f"DATE({column}) = %s")
                params.append(target_date)

        if self._between_filters:
            for column, value_from, value_to in self._between_filters:
                where_clauses.append(f"{column} BETWEEN %s AND %s")
                params.append(value_from)
                params.append(value_to)

        where_clause = ""
        if where_clauses:
            where_clause = " WHERE " + " AND ".join(where_clauses)

        return where_clause, params

    def _build_query(self) -> tuple[str, list]:
        table_name = self._get_table_name(self.model_class)
        where_clause, params = self._build_where_clause()
        query = f"SELECT * FROM {table_name}{where_clause}"

        if self._order_by_value:
            query += f" ORDER BY {self._order_by_value}"

        if self._limit_value is not None:
            query += f" LIMIT {self._limit_value}"

        if self._offset_value:
            query += f" OFFSET {self._offset_value}"

        return query, params

    def list(self, json: bool = False) -> List[T] | List[str]:
        """
        Execute the query and return a list of model instances (sync).
        Always returns a list, even if only one result.
        Automatically rolls back after read to ensure fresh data on next query.

        Args:
            json: If True, return JSON strings instead of model instances (default: False)

        Returns:
            List of model instances or JSON strings
        """
        query, params = self._build_query()

        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                instances = [self.model_class(**row) for row in rows]
                if json:
                    return [instance.model_dump_json() for instance in instances]
                return instances
        finally:
            if not self.conn.autocommit:
                self.conn.rollback()

    async def alist(self, json: bool = False) -> List[T] | List[str]:
        """
        Execute the query and return a list of model instances (async).
        Always returns a list, even if only one result.
        Automatically rolls back after read to ensure fresh data on next query.

        Args:
            json: If True, return JSON strings instead of model instances (default: False)

        Returns:
            List of model instances or JSON strings
        """
        query, params = self._build_query()

        try:
            async with self.conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, params)
                rows = await cur.fetchall()
                instances = [self.model_class(**row) for row in rows]
                if json:
                    return [instance.model_dump_json() for instance in instances]
                return instances
        finally:
            if not self.conn.autocommit:
                await self.conn.rollback()

    def get(self, json: bool = False) -> T | str:
        """
        Execute the query and return a single model instance (sync).
        Raises an exception if more than one result is found.
        Automatically rolls back after read to ensure fresh data on next query.

        Args:
            json: If True, return JSON string instead of model instance (default: False)

        Returns:
            Single model instance or JSON string

        Raises:
            ValueError: If no results found or multiple results found
        """
        if not self._filters:
            raise ValueError("At least one filter must be provided for get()")

        temp_manager = self._clone()
        temp_manager._limit_value = 2
        query, params = temp_manager._build_query()

        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                if len(rows) == 0:
                    raise ValueError(
                        f"No {self.model_class.__name__} found matching the query"
                    )
                elif len(rows) > 1:
                    raise ValueError(
                        f"get() returned more than one {self.model_class.__name__} -- "
                        f"it returned {len(rows)}! Use list() instead."
                    )

                instance = self.model_class(**rows[0])
                if json:
                    return instance.model_dump_json()
                return instance
        finally:
            if not self.conn.autocommit:
                self.conn.rollback()

    async def aget(self, json: bool = False) -> T | str:
        """
        Execute the query and return a single model instance (async).
        Raises an exception if more than one result is found.
        Automatically rolls back after read to ensure fresh data on next query.

        Args:
            json: If True, return JSON string instead of model instance (default: False)

        Returns:
            Single model instance or JSON string

        Raises:
            ValueError: If no results found or multiple results found
        """
        if not self._filters:
            raise ValueError("At least one filter must be provided for get()")

        temp_manager = self._clone()
        temp_manager._limit_value = 2
        query, params = temp_manager._build_query()

        try:
            async with self.conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, params)
                rows = await cur.fetchall()

                if len(rows) == 0:
                    raise ValueError(
                        f"No {self.model_class.__name__} found matching the query"
                    )
                elif len(rows) > 1:
                    raise ValueError(
                        f"get() returned more than one {self.model_class.__name__} -- "
                        f"it returned {len(rows)}! Use list() instead."
                    )

                instance = self.model_class(**rows[0])
                if json:
                    return instance.model_dump_json()
                return instance
        finally:
            if not self.conn.autocommit:
                await self.conn.rollback()

    def count(self) -> int:
        """
        Execute a COUNT query and return the number of matching records (sync).
        This is more efficient than fetching all rows and counting them.
        Respects all filters but ignores LIMIT, OFFSET, and ORDER BY.

        Returns:
            Integer count of matching records

        Example:
            # Count all records
            total = Post.objects.using(conn).count()

            # Count with filters
            active_count = Post.objects.using(conn).find(status="active").count()

            # Count with date filter
            today_count = Post.objects.using(conn).date('created_at', date.today()).count()
        """
        table_name = self._get_table_name(self.model_class)
        where_clause, params = self._build_where_clause()
        query = f"SELECT COUNT(*) as count FROM {table_name}{where_clause}"

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchone()
                return result[0] if result else 0
        finally:
            if not self.conn.autocommit:
                self.conn.rollback()

    async def acount(self) -> int:
        """
        Execute a COUNT query and return the number of matching records (async).
        This is more efficient than fetching all rows and counting them.
        Respects all filters but ignores LIMIT, OFFSET, and ORDER BY.

        Returns:
            Integer count of matching records

        Example:
            # Count all records
            total = await Post.objects.using(conn).acount()

            # Count with filters
            active_count = await Post.objects.using(conn).find(status="active").acount()
        """
        table_name = self._get_table_name(self.model_class)
        where_clause, params = self._build_where_clause()
        query = f"SELECT COUNT(*) as count FROM {table_name}{where_clause}"

        try:
            async with self.conn.cursor() as cur:
                await cur.execute(query, params)
                result = await cur.fetchone()
                return result[0] if result else 0
        finally:
            if not self.conn.autocommit:
                await self.conn.rollback()


class QuerySet(Generic[T]):
    """
    Provides access to the Manager for a model instance.
    Similar to Django's objects attribute.
    """

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def __get__(self, instance, owner) -> "ManagerFactory[T]":
        return ManagerFactory(self.model_class)


class ManagerFactory(Generic[T]):
    """
    Factory that creates Manager instances when given a connection.
    Connection is provided via using() method only.
    """

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def using(self, conn: Any) -> Manager[T]:
        """
        Create a Manager instance with the given connection.
        All subsequent operations use this connection.

        Args:
            conn: Database connection (sync or async)

        Returns:
            Manager instance

        Example:
            Post.objects.using(conn).find(status="published").list()
        """
        return Manager(self.model_class, conn)


class Model(BaseModel):
    """
    Base class for database models with Django-style manager.
    """

    model_config = ConfigDict(from_attributes=True)

    objects: ClassVar[QuerySet] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.objects = QuerySet(cls)

from typing import Optional, Set

from pydantic import BaseModel

from rai_gnns_experimental.common.dataset_model import ColumnDType, ColumnSchema, KeysType, TableSchema, TableType

from .api_request_handler import APIRequestHandler
from .connector import BaseConnector


class ForeignKey(BaseModel):
    """
    Helper class implementing a foreign key entry
    Args:
        column_name (str): Name of the foreign key column
        link_to (str): Table and column name that the foreign key links to.
                    Format: TableName.ColumnName
    """

    column_name: str
    link_to: str

    def __eq__(self, other):
        if isinstance(other, ForeignKey):
            return self.column_name == other.column_name
        return False

    def __hash__(self):
        # hash only on the column name
        # we can not have the same column to link to different tables
        return hash(self.column_name)


class GNNTable:
    """
    Class representing a GNN Table.

    The GNN Table is a metadata class that defines the table attributes that will be used as an input to the GNN
    relational learning engine.
    """

    def __init__(
        self,
        connector: BaseConnector,
        source: str,
        name: str,
        primary_key: str = None,
        foreign_keys: Optional[Set[ForeignKey]] = None,
        time_column: Optional[str] = None,
    ):
        """
        Class constructor for the GNNTable class.

        A table must define either a primary key or at least one foreign key.
        Tables without a primary or foreign key are considered invalid.

        :param connector: The connector object used to interact with the data backend.
        :type connector: Connector

        :param source: The data source. Can be a path to a `.csv` or `.parquet` file,
            or the name of a Snowflake table in the form `<Database.Schema.Table>`.
        :type source: str

        :param primary_key: The name of the primary key column. Note: either a primary key
            or at least one foreign key must be provided.
        :type primary_key: Optional[str]

        :param foreign_keys: A set of foreign keys for the table.
            Note: either a primary key
            or at least one foreign key must be provided.
        :type foreign_keys: Optional[Set[ForeignKey]]

        :param time_column: Optional. The name of the column representing time.
            This can also be set later using the `set_time_column()` method.
        :type time_column: Optional[str]
        """
        self.source = source
        self.name = name

        # initialize loader and read some sample data so we can auto-infer column dtypes
        self.connector = connector

        self.api_handler = APIRequestHandler(connector)
        # fetch data and try to do an initial dtype inferene
        result = self._request_data()

        self.column_names, infered_column_dtypes = result

        # initialize the column schema and the unmapped columns and
        # populate them.
        self._column_schemas = {}
        # set with column names that we can not infer a dtype or that
        # the user has removed
        self._unmapped_columns = set()
        # go through all the dataframe columns
        for col in self.column_names:
            dtype = infered_column_dtypes[col]
            if dtype is not None:  # inference successfull
                col_schema = ColumnSchema(name=col, dtype=dtype)
                self._column_schemas[col] = col_schema
            else:
                self._unmapped_columns.add(col)

        # init placeholders for primary key, foreign keys and time column
        self.primary_key = None
        # init foreign keys as a set to avoid duplicates
        self.foreign_keys = set()
        self.time_column = None

        # try to set primary, foreign key and time columns if specified by user
        # if we fail we will fall back to "set" methods
        if primary_key is not None:
            # error if column does not exist
            self._check_column_existence_on_init(primary_key)
            if primary_key in self._column_schemas:
                self.set_primary_key(col_name=primary_key)
            else:
                print(f"We could not infer the dtype for primary key: {primary_key}")
                print("Please add column manually using the add_column(...) method")
                print("and then set the primary key")

        if foreign_keys is not None:
            for fkey in foreign_keys:
                # error if column does not exist
                self._check_column_existence_on_init(fkey.column_name)
                if fkey.column_name in self._column_schemas:
                    self.set_foreign_key(foreign_key=fkey)
                else:
                    print(f"We could not infer the dtype for foreign key: {fkey}")
                    print("Please add column manually using the add_column(...) method")
                    print("and then set the foreign key")

        if time_column is not None:
            # error if column does not exist
            self._check_column_existence_on_init(time_column)
            if time_column in self._column_schemas:
                if self._column_schemas[time_column].dtype == ColumnDType.datetime_t:
                    self.set_time_column(col_name=time_column)
                else:
                    print(f"Automatic inference of dtype for {time_column} failed")
                    print("Column dtype was assigned to: {self._column_schemas[time_column].dtype}")
                    print("Please change the column dtype and then set the time column")
            else:
                print(f"We could not infer the dtype for time column: {time_column}")
                print("Please add column manually using the add_column(...) method")
                print("and then set the time column")

    def update_column_dtype(self, col_name: str, dtype: ColumnDType):
        """
        Update the data type of existing column in the GNN table.

        The column must already exist in the table. If it does not, it must be added first.

        :param col_name: The name of the column to update.
        :type col_name: str
        :param dtype: The new data type to assign to the column.
        :type dtype: ColumnDtype
        :raises ValueError: If the column does not exist in the GNN table.
        :raises ValueError: If the column is a time column and the new dtype is not a datetime.
        """
        if col_name not in self._column_schemas:
            self._raise_error_col_not_in_meta(col_name)
        if self.time_column == col_name and dtype != ColumnDType.datetime_t:
            raise ValueError(f"❌ Column {col_name} is a time column, and only dtype of datetime is allowed")
        self._column_schemas[col_name].dtype = dtype.value

    def remove_column(self, col_name: str):
        """
        Remove an existing column from the GNN table.

        If the column is used as a primary key, foreign key, or time column, it will be removed from those roles as
        well.

        :param col_name: The name of the column to remove from the GNN table.
        :type col_name: str
        :raises ValueError: If the column does not exist in the GNN table.
        """
        if col_name not in self._column_schemas:
            self._raise_error_col_not_in_meta(col_name)
        self._column_schemas.pop(col_name)
        self._unmapped_columns.add(col_name)
        # if column was a time column remove it
        if self.time_column == col_name:
            self.time_column = None
        # if column was a primary key remove it
        if self.primary_key == col_name:
            self.primary_key = None
        # if column was a foreign key remove it
        fkeys_to_remove = set()
        if self.foreign_keys is not None:
            for fkey in self.foreign_keys:
                if fkey.column_name == col_name:
                    fkeys_to_remove.add(fkey)
            self.foreign_keys.difference_update(fkeys_to_remove)

    def add_column(self, col_name: str, dtype: ColumnDType):
        """
        Add a column that exists in the original dataset but not yet in the GNN table.

        :param col_name: The name of the column to add.
        :type col_name: str
        :param dtype: The data type of the column.
        :type dtype: ColumnDType
        :raises ValueError: If the column is already part of the GNN table.
        :raises ValueError: If the column does not exist in the original dataset.
        """
        if col_name in self._column_schemas:
            raise ValueError(
                f"❌ {col_name} is already in the GNN table, use set/unset methods to change its values. "
                f"Columns not part of the GNN table: {self._unmapped_columns}"
            )
        elif col_name not in self._unmapped_columns:
            raise ValueError(
                f"❌ {col_name} is not part of the data. " f"Columns not part of the GNN table: {self._unmapped_columns}"
            )

        self._column_schemas[col_name] = ColumnSchema(name=col_name, dtype=dtype.value)
        self._unmapped_columns.discard(col_name)

    def set_primary_key(self, col_name: str):
        """
        Set an existing column in the GNN table as the primary key.

        If another primary key is already set, it will be replaced by the new one.

        :param col_name: The name of the existing column to set as the primary key.
        :type col_name: str
        :raises ValueError: If the column does not exist in the GNN table.
        """

        if col_name not in self._column_schemas:
            self._raise_error_col_not_in_meta(col_name)
        # unset primary key if we already have one
        if self.primary_key is not None:
            self.unset_primary_key(self.primary_key)
        self.primary_key = col_name
        self._column_schemas[col_name].key_type = KeysType.primary_key.value
        # make sure that it is not a foreign key any more
        self._column_schemas[col_name].link_to = None

    def unset_primary_key(self, col_name: str):
        """
        Unset an existing column as the primary key in the GNN table.

        This will remove the column from its role as the primary key.

        :param col_name: The name of the existing column to unset as the primary key.
        :type col_name: str
        :raises ValueError: If the column does not exist in the GNN table.
        :raises KeyError: If the column is not currently set as the primary key.
        """

        if col_name not in self._column_schemas:
            self._raise_error_col_not_in_meta(col_name)
        if self.primary_key == col_name:
            self.primary_key = None
            self._column_schemas[col_name].key_type = None
        else:
            raise KeyError(f"❌ {col_name} is not a primary key. Current primary key set to {self.primary_key}")

    def set_foreign_key(self, foreign_key: ForeignKey):
        """
        Set an existing column in the GNN table as a foreign key.

        :param foreign_key: The foreign key definition to apply.
        :type foreign_key: ForeignKey
        :raises ValueError: If the referenced column does not exist in the GNN table.
        """

        col_name = foreign_key.column_name
        link_to = foreign_key.link_to
        if col_name not in self._column_schemas:
            self._raise_error_col_not_in_meta(col_name)
        if foreign_key in self.foreign_keys:
            raise ValueError(
                "❌ Duplicate foreign keys detected, please unset column as a foreign key and try again. "
                f"Current foreign keys {self.foreign_keys} "
                f"Trying to set duplicate key with column name: {foreign_key.column_name}"
            )
        self.foreign_keys.add(foreign_key)
        self._column_schemas[col_name].key_type = KeysType.foreign_key.value
        self._column_schemas[col_name].link_to = link_to

    def unset_foreign_key(self, foreign_key: ForeignKey):
        """
        Set an existing column in the GNN table as a foreign key.

        :param foreign_key: The foreign key definition to apply.
        :type foreign_key: ForeignKey
        :raises ValueError: If the referenced column does not exist in the GNN table.
        :raises KeyError: If the foreign key is not part of the declared foreign keys.
        """

        col_name = foreign_key.column_name
        if col_name not in self._column_schemas:
            self._raise_error_col_not_in_meta(col_name)
        if foreign_key not in self.foreign_keys:
            raise KeyError(f"❌ Foreign key {foreign_key} does not exist " f"Current coreign keys: {self.foreign_keys}")
        self.foreign_keys.remove(foreign_key)
        self._column_schemas[col_name].key_type = None
        self._column_schemas[col_name].link_to = None

    def set_time_column(self, col_name: str):
        """
        Set an existing column in the GNN table as the time column.

        If a different time column is already set, it will be replaced.

        :param col_name: The name of the existing column to set as the time column.
        :type col_name: str
        :raises ValueError: If the column does not exist in the GNN table.
        :raises ValueError: If the column's data type is not datetime.
        """

        if col_name not in self._column_schemas:
            self._raise_error_col_not_in_meta(col_name)
        if self._column_schemas[col_name].dtype != ColumnDType.datetime_t:
            raise ValueError(
                f"❌ Column {col_name} has dtype {self._column_schemas[col_name].dtype}. "
                "Only datetime columns can be used as time columns"
            )
        self.time_column = col_name

    def unset_time_column(self, col_name: str):
        """
        Unset an existing column as the time column in the GNN table.

        :param col_name: The name of the existing column to unset as the time column.
        :type col_name: str
        :raises ValueError: If the column does not exist in the GNN table.
        :raises ValueError: If the column is not currently set as the time column.
        """
        if col_name not in self._column_schemas:
            self._raise_error_col_not_in_meta(col_name)

        if self.time_column == col_name:
            self.time_column = None
        else:
            raise ValueError(f"❌ {col_name} is not a time column, current time column set to {self.time_column}")

    def validate_table(self):
        """
        Helper function that performs various tests to validate metadata.

        Checks:
            - If there are any unmapped or unused columns.
            - If the table has at least one primary key or one foreign key.

        :raises ValueError: If no primary or foreign keys are present.
        :raises ValueError: If a foreign key is set as a time column.
        :raises ValueError: If a primary key is set as a time column.
        """
        if len(self._unmapped_columns) > 0:
            print(f"Some columns where either removed or missing. Columns: {self._unmapped_columns}")
            print("To include these columns in your dataset, please add them manually using the 'add_column' method.")

        if self.primary_key is None and (self.foreign_keys is None or len(self.foreign_keys) == 0):
            raise ValueError(
                f"❌ Table: '{self.name}' has no primary or foreign key columns "
                "Please set foreign or primary key columns"
            )
        # check to see if the time column is a primary or foreign key
        if self.time_column is not None:
            if self.primary_key is not None and self.time_column == self.primary_key:
                raise ValueError(
                    f"❌ Table '{self.name}' has a primary key that is also a time column. "
                    "Operation not allowed: a primary key can not be a time column."
                )
            if self.foreign_keys is not None:
                for fkey in self.foreign_keys:
                    if fkey.column_name == self.time_column:
                        raise ValueError(
                            f"❌ Table '{self.name}' has a foreign key {fkey.column_name} that is also a time column. "
                            "Operation not allowed: a foreign key can not be a time column."
                        )

    def show_table(self):
        """Pretty print the table metadata schema and table details."""
        table_schema = self._create_table_schema(validate=False)
        print(table_schema.table_info)

    def _create_table_schema(self, validate: bool = True) -> TableSchema:
        """Create the table metadata."""
        if validate:
            self.validate_table()
        table_schema = TableSchema(
            name=self.name,
            source=self.source,
            type=TableType.NODE,
            columns=list(self._column_schemas.values()),
            time_column=self.time_column,
        )
        return table_schema

    def _check_column_existence_on_init(self, col_name: str):
        """
        Checks if the col_name exists on the sample data dataframe, throws an assertion error if it does not exist.

        Called only upon class initialization
        Args:
            col_name (str): The name of the column
        Raise:
            ValueError: If col_name does not exist in the data
        """
        if col_name not in self.column_names:
            raise ValueError(f"❌ Column: {col_name} does not exist in the data")

    def _request_data(self):
        """
        Ping the rest API to fetch data.

        Args:
            timeout (int): Timeout in seconds to await for the request to return data
        Returns:
            columns (List[str]): A list with the column names
            column_dtypes (Dict[str, ColumnDType]): A dict with the column dtypes
                that where successfully infered (if we can not infer a column dtype
                then that column will not appear in this dictionary)
        """
        payload = {
            "payload_type": "FETCH_TABLE",
            "source": self.source,
            "connector": self.connector.connector_type,
        }

        json_data = self.api_handler.make_request(payload, [self.source])
        column_names = json_data["columns"]
        column_dtypes = json_data["dtypes"]
        return column_names, column_dtypes

    def _raise_error_col_not_in_meta(self, col_name: str):
        """
        Raise value error if column name is not in GNN table metadata
        Args:
            col_name (str): The column name
        """
        raise ValueError(
            f"❌ {col_name} is not part of the GNN table "
            f"GNN Table columns: {self._column_schemas.keys()} "
            f"Columns not part of the GNN table: {self._unmapped_columns}"
        )

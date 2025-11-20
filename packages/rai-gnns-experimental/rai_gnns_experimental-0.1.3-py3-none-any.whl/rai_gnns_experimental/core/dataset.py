import json
from copy import deepcopy
from typing import Dict, List, Union

import sqlalchemy
from sqlalchemy import Column, ForeignKey, MetaData, Table, create_engine

from rai_gnns_experimental.common.dataset_model import ColumnDType, ColumnSchema, KeysType
from rai_gnns_experimental.external.db_diagram import create_schema_graph

from .connector import BaseConnector
from .custom_sqlalchemy_dtypes import (
    CustomARRAY,
    CustomBLOB,
    CustomDateTime,
    CustomFloat,
    CustomInteger,
    CustomString,
    CustomVARCHAR,
)
from .gnn_table import GNNTable
from .task import LinkTask, NodeTask, TaskType


class Dataset:
    """
    Wrapper class to DatasetBuilder.

    Main functionality is to compile a .json metadata file that can be used for instantiating the DatasetBuilder and
    MetadataTaskParser classes. Also implements logic to test for inconsistencies such as tabley key inconsistencies or
    time column errors
    """

    def __init__(
        self,
        connector: BaseConnector,
        dataset_name: str,
        tables: List[GNNTable],
        task_description: Union[NodeTask, LinkTask],
    ):
        """
        Initializes the dataset and loads task and dataset data.

        :param connector: The connector object used for interacting with the data backend.
        :type connector: str

        :param dataset_name: The name of the dataset.
        :type dataset_name: str

        :param tables: A list of table objects that are part of the dataset.
        :type tables: List[GNNTable]

        :param task_description: The task for the GNN, either a `NodeTask` or a `LinkTask`.
        :type task_description: Union[NodeTask, LinkTask]
        """
        self.connector = connector
        self.dataset_name = dataset_name
        self.tables = tables
        self.task_description = task_description
        # Construct metadata dict
        self._run_sanity_checks()
        # init. from create dataset
        self.experiment_name = "_".join(
            (self.dataset_name, self.task_description.task_type.value, self.task_description.name)
        )
        self.metadata_dict = self._construct_metadata_dict()

    def visualize_dataset(self, show_dtypes: bool = False):
        """
        Helper function to visualize the dataset. Returns a `pydot.core.dot` graph object that can be visualized in an
        IPython notebook.

        Example usage:
            from IPython.display import Image, display
            graph = dataset.visualize_dataset()
            plt = Image(graph.create_png())
            display(plt)

        :param show_dtypes: Optional. Whether to show the SQLAlchemy dtypes of each column.
            Default is `False`.
        :type show_dtypes: bool

        :returns: A graph visualization object of the dataset.
        :rtype: pydot.core.dot
        """

        sql_alch_meta = self._create_sql_alchemy_metadata
        graph = create_schema_graph(
            engine=create_engine("sqlite://"),  # Use a temporary in-memory sqlite db.
            metadata=sql_alch_meta,
            show_datatypes=show_dtypes,
            show_indexes=False,
            rankdir="TB",
            concentrate=True,
        )
        return graph

    def print_data_config(self):
        """Prints the final dataset config."""
        print(json.dumps(self.metadata_dict, indent=4))

    def _column_to_dict(self, column: ColumnSchema) -> Dict:
        """
        Helper function to convert a ColumnSchema to a dict
        Args:
            column (ColumnSchema):  The column to extract data from
        """
        column_dict = {}
        column_dict["name"] = column.name
        column_dict["dtype"] = column.dtype
        if column.key_type is not None:
            column_dict["key_type"] = column.key_type
            if column.key_type == "foreign_key":
                column_dict["link_to"] = column.link_to
        if column.format is not None:
            column_dict["format"] = column.format
        return column_dict

    def _construct_metadata_dict(self) -> Dict:
        """Construct the metadata dictionary."""
        metadata_dict = {
            "connector": {
                "name": self.connector.connector_type,
                "dataset_name": self.dataset_name,
                "experiment_name": self.experiment_name,
            }
        }
        metadata_dict["tables"] = []
        # add table information
        for table in self.tables:
            table_meta_dict = {}
            table_meta_dict["name"] = table.name
            table_meta_dict["source"] = table.source
            table_meta_dict["type"] = "node"
            table_meta_dict["extra_fields"] = {}
            if table.time_column is not None:
                table_meta_dict["time_column"] = table.time_column
            table_meta_dict["columns"] = []
            # add table column information
            for column in table._column_schemas.values():
                table_meta_dict["columns"].append(self._column_to_dict(column))
            metadata_dict["tables"].append(table_meta_dict)
        # add task information
        metadata_dict["task"] = {}
        metadata_dict["task"]["name"] = self.task_description.name
        metadata_dict["task"]["source"] = self.task_description.task_data_source
        metadata_dict["task"]["columns"] = []

        for column in self.task_description.table_schema.columns:
            metadata_dict["task"]["columns"].append(self._column_to_dict(column))

        if self.task_description.time_column is not None:
            metadata_dict["task"]["time_column"] = self.task_description.time_column

        metadata_dict["task"]["task_type"] = self.task_description.task_type.value
        metadata_dict["task"]["current_time"] = self.task_description.current_time

        if self.task_description.task_type_dict[self.task_description.task_type] == "node":
            metadata_dict["task"]["target_column"] = self.task_description.target_column
            metadata_dict["task"]["target_table"] = self.task_description.source_entity_table
            metadata_dict["task"]["evaluation_metric"] = {"name": self.task_description.evaluation_metric.name}
        else:
            metadata_dict["task"]["source_column"] = self.task_description.source_entity_column
            metadata_dict["task"]["source_table"] = self.task_description.source_entity_table
            metadata_dict["task"]["target_column"] = self.task_description.target_entity_column
            metadata_dict["task"]["target_table"] = self.task_description.target_entity_table
            metadata_dict["task"]["evaluation_metric"] = {
                "name": self.task_description.evaluation_metric.name,
                "eval_at_k": self.task_description.evaluation_metric.eval_at_k,
            }

        return metadata_dict

    def _run_sanity_checks(self):
        """Runs sanity all checks."""
        # validate all tables
        for table in self.tables:
            table.validate_table()
        self._check_time_column_consistency()
        self._check_pkey_fkey_consistency()
        self._check_db_connectivity()
        if self.task_description.task_type in [TaskType.LINK_PREDICTION, TaskType.REPEATED_LINK_PREDICTION]:
            self._check_link_task_consistency()
        else:
            self._check_node_task_consistency()

    def _check_time_column_consistency(self):
        """
        If a time column has been defined in the task, but
        there's no time column defined in the data, throw
        an error (and vice versa)
        Raises:
            ValueError: If time column does not exist in data tables
                but exists in task table
            ValueError: If the time column does exist in the data
                tables but does not exist in the task table

        """
        time_col_table = None
        for table in self.tables:
            if table.time_column is not None:
                time_col_table = table.name
                break
        # task has time column data does not
        if self.task_description.time_column is not None and time_col_table is None:
            raise ValueError(
                f"❌ task has a data time column defined: {self.task_description.time_column}"
                " but there is no time column defined in the data tables"
            )
        # task does not have a time column but data has
        if self.task_description.time_column is None and time_col_table is not None:
            raise ValueError(
                "❌ task has no data time column defined, but at least one "
                f"data table {time_col_table} has a time column"
            )

    def _construct_table_dict(self) -> Dict[str, GNNTable]:
        """
        Helper function that scans through the data tables and returns a table dict.

        Returns:
            table_dict (Dict[str,GNNTable]): Key: table name, value: GNNTable
        """
        table_dict = {}
        for table in self.tables:
            table_dict[table.name] = table
        return table_dict

    def _check_pkey_fkey_consistency(self):
        """
        Checks if the data tables have consistent primary and foreign keys
        Raises:
            ValueError: If foreign keys point to non existent primary keys
        """
        # start by constructing a helper dict that will map tables to table names
        table_dict = self._construct_table_dict()
        for table in self.tables:
            if table.foreign_keys is not None:
                fkeys = table.foreign_keys
                for fkey in fkeys:
                    link_to = fkey.link_to.split(".")
                    if len(link_to) != 2:
                        raise ValueError(f"❌ Badly formatted foreign key: {fkey}")
                    table_name, pkey_name = link_to[0], link_to[1]
                    if table_name not in table_dict:
                        raise ValueError(
                            f"❌ Foreign key {fkey.column_name} points to table {table_name} "
                            "however there does not exist such a table"
                        )
                    if table_dict[table_name].primary_key != pkey_name:
                        raise ValueError(
                            f"❌ Foreign key {fkey.column_name} points "
                            f"to primary key {pkey_name} in table {table_name}. However "
                            f"{table_name} does not have a primary key column {pkey_name}"
                        )

    def _check_db_connectivity(self):
        """
        Check if the database tables form a connected graph.

        Here we do not care if foreign keys point to non-existent
        primary keys since we can "catch" that with the _check_pkey_fkey_consistency call
        Raises:
            ValueError if the database tables are not connected
        """
        # start by constructing a helper dict that will map tables to table names
        table_dict = self._construct_table_dict()
        # now we will instantiate an undirected graph where the key will
        # be a table name and values will be a list of tables that connect to
        # that table
        graph = {}
        # add nodes
        for table_name in table_dict:
            graph[table_name] = []
        # add indirected edges
        for source_table_name, table in table_dict.items():
            if table.foreign_keys is not None:
                # edges are essentially defined by fkeys
                fkeys = table.foreign_keys
                for fkey in fkeys:
                    link_to = fkey.link_to.split(".")
                    dest_table_name = link_to[0]
                    # add edge
                    graph[source_table_name].append(dest_table_name)
                    graph[dest_table_name].append(source_table_name)
        # now we can simply implement depth first search to see if we are connected
        # set with visited nodes
        visited = set()
        # start node - any node will do
        start_node = next(iter(graph))

        def dfs(node):
            """Helper recursive depth-first search."""
            visited.add(node)
            for neigh in graph.get(node, []):
                if neigh not in visited:
                    dfs(neigh)

        dfs(start_node)
        if len(visited) != len(graph):
            raise ValueError(
                f"❌ Found the following tables in the database: {list(graph)}. "
                "The database does not seem to be connected. "
                "Please make sure to add proper primary and foreign keys to establish connections"
            )

    def _check_link_task_consistency(self):
        """
        Checks if source/target entity table of link task exists
        Checks if source/target entity column of a link task is a primary key
            in the corresponding table
        Raises:
            ValueError: If source entity table does not exist in database tables
            ValueError: If source entity column is not a primary key in the
                corresponding table
            ValueError: If target entity table does not exist in database tables
            ValueError: If target entity column is not a primary key in the
                corresponding table
        """
        table_dict = self._construct_table_dict()
        # since column names might differ we need to get the values
        # from the foreign key description instead of getting them
        # directly from the source_entyty_column or source_entity_table
        src_fkey = None
        tgt_fkey = None
        for key in self.task_description.foreign_keys:
            if key.column_name == self.task_description.source_entity_column:
                src_fkey = key.link_to.split(".")
                src_table = src_fkey[0]
                src_col = src_fkey[1]
            elif key.column_name == self.task_description.target_entity_column:
                tgt_fkey = key.link_to.split(".")
                tgt_table = tgt_fkey[0]
                tgt_col = tgt_fkey[1]
        if src_fkey is None or tgt_fkey is None:
            raise ValueError("❌ Please set the foreign keys of the task table")

        if src_table in table_dict:
            if src_col != table_dict[src_table].primary_key:
                raise ValueError(
                    f"❌ The source entity column: {src_col} does not exist "
                    f"in the corresponding database table: {src_table}"
                )
        else:
            raise ValueError(f"❌ The source entity table {src_table} does not exist" " in the database tables")

        if tgt_table in table_dict:
            if tgt_col != table_dict[tgt_table].primary_key:
                raise ValueError(
                    f"❌ The source entity column: {tgt_col} does not exist "
                    f"in the corresponding database table: {tgt_table}"
                )
        else:
            raise ValueError(f"❌ The source entity table {tgt_table} does not exist" " in the database tables")

    def _check_node_task_consistency(self):
        """
        Checks if source entity table of node task exists
        Checks if source entity column of node task is a primary key
            in the corresponding table
        Raises:
            ValueError: If source entity table does not exist in database tables
            ValueError: If source entity column is not a primary key in the
                corresponding table
        """
        table_dict = self._construct_table_dict()
        src_table = self.task_description.source_entity_table
        src_col = self.task_description.source_entity_column
        if src_table in table_dict:
            if src_col != table_dict[src_table].primary_key:
                raise ValueError(
                    f"❌ The source entity column: {src_col} does not exist "
                    f"in the corresponding database table: {src_table}"
                )
        else:
            raise ValueError(f"❌ The source entity table {src_table} does not exist" " in the database tables")

    @property
    def _create_sql_alchemy_metadata(self) -> sqlalchemy.MetaData:
        """
        Create sql achemy metadata describing the table and the task.

        Returns:
            metadata (sqlalchemy.MetaData): The sql alchemy metadata
        """
        metadata = MetaData()
        # create the database tables
        for table in self.tables:
            table_name = table.name
            cols = []
            for col_name, col_schema in table._column_schemas.items():
                col = self._make_sqlalchemy_column(col_name, col_schema)
                cols.append(col)
            # here essentially we dynamicaly update metadata
            _ = Table(table_name, metadata, *cols)
        # add task
        task_cols = []
        for col_name, col_schema in self.task_description._column_schemas.items():
            if (
                self.task_description.task_type_dict[self.task_description.task_type] == "node"
                and col_schema.key_type == KeysType.primary_key
            ):
                viz_col_schema = deepcopy(col_schema)
                viz_col_schema.key_type = "foreign_key"
                viz_col_schema.link_to = (
                    f"{self.task_description._source_entity_table}.{self.task_description._source_entity_column}"
                )
                col = self._make_sqlalchemy_column(col_name, viz_col_schema)
            else:
                col = self._make_sqlalchemy_column(col_name, col_schema)
            task_cols.append(col)
        _ = Table(self.task_description.name, metadata, *task_cols)
        return metadata

    def _make_sqlalchemy_column(self, col_name: str, col_schema: ColumnSchema) -> Column:
        """
        Helper function to create an sclalchemy table column
        Args:
            col_name (str): The column name
            col_schema (ColumnSchema): The column schema
        Reutrn:
            col (Column): The SQL alchemy column
        Raise:
            ValueError: if the col_type is not a known ColumnDType
        """
        dtype_mapping_dict = {
            ColumnDType.category_t: CustomVARCHAR,
            ColumnDType.datetime_t: CustomDateTime,
            ColumnDType.embedding_t: CustomBLOB,
            ColumnDType.float_t: CustomFloat,
            ColumnDType.integer_t: CustomInteger,
            ColumnDType.multi_category_t: CustomARRAY,
            ColumnDType.text_t: CustomString,
        }

        col_type = col_schema.dtype
        key_type = col_schema.key_type
        is_pkey = False
        link_to = None
        if key_type == KeysType.primary_key:
            is_pkey = True
        elif key_type == KeysType.foreign_key:
            link_to = col_schema.link_to
            # foreign/primary keys will overwrite column dtypes
            # and go first
        if is_pkey:
            col = Column(col_name, dtype_mapping_dict[col_type](), primary_key=True)
        elif link_to is not None:
            col = Column(col_name, dtype_mapping_dict[col_type](), ForeignKey(link_to))
        else:
            if col_type in dtype_mapping_dict:
                col = Column(col_name, dtype_mapping_dict[col_type]())
            else:
                raise ValueError(f"❌ Unknown column dtype {col_type}")
        return col

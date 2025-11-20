from abc import abstractmethod
from typing import Dict, Literal, Optional

from rai_gnns_experimental.common.dataset_model import ColumnDType, EvaluationMetric, TaskMeta, TaskType

from .connector import BaseConnector
from .gnn_table import ForeignKey, GNNTable
from .utils import CustomAttributeError

__all__ = ["TaskType"]


class Task(GNNTable):
    """
    Base class to define all kinds of tasks.

    Inherits from Table to implement logic of adding primary/foreign key columns, time columns and determine dtypes
    """

    # helper dict to differentiate different task types (node vs link)
    task_type_dict = {
        TaskType.LINK_PREDICTION: "link",
        TaskType.REPEATED_LINK_PREDICTION: "link",
        TaskType.BINARY_CLASSIFICATION: "node",
        TaskType.MULTICLASS_CLASSIFICATION: "node",
        TaskType.MULTILABEL_CLASSIFICATION: "node",
        TaskType.REGRESSION: "node",
    }

    task_data_source: Dict[Literal["train", "test", "validation"], str]

    def __init__(
        self,
        connector: BaseConnector,
        name: str,
        task_data_source: Dict[Literal["train", "test", "validation"], str],
        task_type: TaskType,
        time_column: Optional[str] = None,
        target_column: Optional[str] = None,
        source_entity_column: Optional[str] = None,
        source_entity_table: Optional[str] = None,
        target_entity_column: Optional[str] = None,
        target_entity_table: Optional[str] = None,
        evaluation_metric: Optional[EvaluationMetric] = None,
        current_time: Optional[bool] = True,
    ):
        """
        Base class describing a task.

        Inherits from the Table class.
        Args:
            connector (str): A connector object
            name (str): The name of the task, can be anything describing the task at hand
            task_data_source (Dict[Literal["train","test","validation"], str]): A dictionary with
                    three keys: "train","test","validation" pointing to the path of the train/test and validation
                    datasets. The path can be a  path to a .csv / .parquet file or the name
                    of a snowflake table <Database.Schema.Path>
            time_column (str): Optional. The name of the time column. Can also be set later
                        using the set_time_column function
            target_column (str). Optional. The name of the target column for node classification tasks.
                        The target column is the column of a task table holding the values that will
                        be used to train the model
            source_entity_column (str): Optional. The name of the source entity column in link prediction tasks
            source_entity_table (str): Optional. The name of the source entity table in link prediction tasks OR the
                                    name of the source entity table in node tasks
            target_entity_column (str): Optional. The name of the target entity column in link prediction tasks
            target_entity_table (str): Optional. The name of the target entity table in link prediction tasks
            evaluation_metric (EvaluationMetric): Optional. The name of the evaluation metric that
                                 we want to optimize for
            current_time (bool): Optional. If set to False the current time of the task table will be reduced
                    by one time unit. Useful when the time column at the task table does not need to see the
                    values from the database tables at the same time stamp
        """
        # init primary and foreign keys as empty
        foreign_keys = None
        primary_key = None
        # high level checks based on tasks
        if self.task_type_dict[task_type] == "node":
            # set primary key as the source entity column
            primary_key = source_entity_column
        else:
            # set the foreign keys as the source/target destination columns
            source_fkey = ForeignKey(
                column_name=source_entity_column, link_to=f"{source_entity_table}.{source_entity_column}"
            )
            dest_fkey = ForeignKey(
                column_name=target_entity_column, link_to=f"{target_entity_table}.{target_entity_column}"
            )
            foreign_keys = set([source_fkey, dest_fkey])

        super().__init__(
            connector=connector,
            source=task_data_source["train"],
            name=name,
            primary_key=primary_key,
            foreign_keys=foreign_keys,
            time_column=time_column,
        )
        # create task tables shema and see if there are any errors
        self.table_schema = self._create_table_schema(validate=True)

        self.task_data_source = task_data_source  # table data source for /train/test/val
        self.task_type = task_type  # task type
        self._target_column = target_column  # target column for node related tasks
        # make sure that the target column exists in the dataframe
        if self.target_column is not None and self.target_column not in list(self._column_schemas.keys()):
            raise ValueError(f"❌ Target column: {self.target_column} does not exist in the task table")
        # source entity table for node and link tasks
        self._source_entity_table = source_entity_table
        # source entity column for link tasks,  for node tasks this is the same as the primary key name
        self._source_entity_column = source_entity_column
        # target entity table: link prediction
        self._target_entity_table = target_entity_table
        # target entity column: link prediction
        self._target_entity_column = target_entity_column
        # evaluation metrics for task
        self.evaluation_metric = evaluation_metric
        # set current time for task
        self._current_time = current_time

        if self.evaluation_metric is None:
            self._set_default_eval_metric()
            print(f"No evaluation metric detected, defaulting to {self.evaluation_metric.name}")

    def set_evaluation_metric(self, evaluation_metric: EvaluationMetric):
        """
        Helper function to set the evaluation metric.

        :param evaluation_metric: The name of the evaluation metric to optimize for. Optional.
        :type evaluation_metric: EvaluationMetric
        """
        if self.task_type_dict[self.task_type] == "link" and evaluation_metric.eval_at_k is None:
            self.evaluation_metric = EvaluationMetric(name=evaluation_metric.name, eval_at_k=12)
        else:
            self.evaluation_metric = evaluation_metric

    def _set_default_eval_metric(self):
        """Helper function to return a default evaluation metric, if not specified by the user."""
        if self.evaluation_metric is None:
            if self.task_type == TaskType.REGRESSION:
                self.evaluation_metric = EvaluationMetric(name="rmse")
            elif self.task_type == TaskType.BINARY_CLASSIFICATION:
                self.evaluation_metric = EvaluationMetric(name="roc_auc")
            elif self.task_type == TaskType.LINK_PREDICTION or self.task_type == TaskType.REPEATED_LINK_PREDICTION:
                self.evaluation_metric = EvaluationMetric(name="link_prediction_map", eval_at_k=12)
            elif self.task_type == TaskType.MULTICLASS_CLASSIFICATION:
                self.evaluation_metric = EvaluationMetric(name="macro_f1")
            else:
                self.evaluation_metric = EvaluationMetric(name="multilabel_auroc_macro")

    @abstractmethod
    def show_task(self):
        """Pretty print task information."""
        pass

    @abstractmethod
    def _create_task(self):
        """Helper function to create TaskMeta."""
        pass

    # --- Override functions to update self.table_schema -----#
    def update_column_dtype(self, col_name: str, dtype: ColumnDType):
        super().update_column_dtype(col_name, dtype)
        self.table_schema = self._create_table_schema(validate=False)

    def remove_column(self, col_name: str):
        super().remove_column(col_name)
        self.table_schema = self._create_table_schema(validate=False)

    def add_column(self, col_name: str, dtype: ColumnDType):
        super().add_column(col_name, dtype)
        self.table_schema = self._create_table_schema(validate=False)

    def set_primary_key(self, col_name: str):
        super().set_primary_key(col_name)
        self.table_schema = self._create_table_schema(validate=False)

    def unset_primary_key(self, col_name: str):
        super().unset_primary_key(col_name)
        self.table_schema = self._create_table_schema(validate=False)

    def set_foreign_key(self, foreign_key: ForeignKey):
        super().set_foreign_key(foreign_key)
        self.table_schema = self._create_table_schema(validate=False)

    def unset_foreign_key(self, foreign_key: ForeignKey):
        super().unset_foreign_key(foreign_key)
        self.table_schema = self._create_table_schema(validate=False)

    def set_time_column(self, col_name: str):
        super().set_time_column(col_name)
        self.table_schema = self._create_table_schema(validate=False)

    def unset_time_column(self, col_name: str):
        super().unset_time_column(col_name)
        self.table_schema = self._create_table_schema(validate=False)

    @property
    def target_column(self):
        return self._target_column

    @target_column.setter
    def target_column(self, value):
        raise CustomAttributeError("❌ Cannot set 'target_column' after initialization. It is read-only.")

    @property
    def source_entity_column(self):
        return self._source_entity_column

    @source_entity_column.setter
    def source_entity_column(self, value):
        raise CustomAttributeError("❌ Cannot set 'source_entity_column' after initialization. It is read-only.")

    @property
    def source_entity_table(self):
        return self._source_entity_table

    @source_entity_table.setter
    def source_entity_table(self, value):
        raise CustomAttributeError("❌ Cannot set 'source_entity_table' after initialization. It is read-only.")

    @property
    def target_entity_column(self):
        return self._target_entity_column

    @target_entity_column.setter
    def target_entity_column(self, value):
        raise CustomAttributeError("❌ Cannot set 'target_entity_column' after initialization. It is read-only.")

    @property
    def target_entity_table(self):
        return self._target_entity_table

    @target_entity_table.setter
    def target_entity_table(self, value):
        raise CustomAttributeError("❌ Cannot set 'target_entity_table' after initialization. It is read-only.")

    @property
    def current_time(self):
        return self._current_time

    @current_time.setter
    def current_time(self, value):
        raise CustomAttributeError("❌ Cannot set 'current_time' after initialization. It is read-only.")


class LinkTask(Task):
    """
    Class representing link based tasks.

    It can be used for classic or repeater link prediction tasks.
    """

    def __init__(
        self,
        connector: BaseConnector,
        name: str,
        task_data_source: Dict[Literal["train", "test", "validation"], str],
        source_entity_column: str,
        source_entity_table: str,
        target_entity_column: str,
        target_entity_table: str,
        task_type: Literal[TaskType.LINK_PREDICTION, TaskType.REPEATED_LINK_PREDICTION],
        time_column: Optional[str] = None,
        evaluation_metric: Optional[EvaluationMetric] = None,
        current_time: Optional[bool] = True,
    ):
        """
        Link task.

        :param connector: The connector object used for interacting with the data backend.
        :type connector: str

        :param name: The name of the task, which can describe the task at hand.
        :type name: str

        :param task_data_source: A dictionary with three keys: "train", "test", and "validation",
            each pointing to the path of the respective dataset. The path can be a `.csv` or `.parquet` file,
            or the name of a Snowflake table in the form `<Database.Schema.Table>`.
        :type task_data_source: Dict[Literal["train", "test", "validation"], str]

        :param source_entity_column: The name of the source entity column in link prediction tasks.
        :type source_entity_column: str

        :param source_entity_table: The name of the source entity table in link prediction tasks,
            or the name of the source entity table in node tasks.
        :type source_entity_table: str

        :param target_entity_column: The name of the target entity column in link prediction tasks.
        :type target_entity_column: str

        :param target_entity_table: The name of the target entity table in link prediction tasks.
        :type target_entity_table: str

        :param task: The type of the task, which can be either link prediction or repeated link prediction.
        :type task: Literal[TaskType.LINK_PREDICTION, TaskType.REPEATED_LINK_PREDICTION]

        :param time_column: Optional. The name of the time column. This can also be set later
            using the `set_time_column` function.
        :type time_column: Optional[str]

        :param evaluation_metric: Optional. The name of the evaluation metric to optimize for.
        :type evaluation_metric: Optional[EvaluationMetric]

        :param current_time: Optional. If set to False the current time of the task table will be reduced
                    by one time unit. Useful when the time column at the task table does not need to see the
                    values from the database tables at the same time stamp
        :type current_time: Optional[bool]
        """

        super().__init__(
            connector=connector,
            name=name,
            task_data_source=task_data_source,
            task_type=task_type,
            time_column=time_column,
            source_entity_column=source_entity_column,
            source_entity_table=source_entity_table,
            target_entity_column=target_entity_column,
            target_entity_table=target_entity_table,
            evaluation_metric=evaluation_metric,
            current_time=current_time,
        )
        # to be filled when create_task is called
        self.task_info = self._create_task()

    def _create_task(self) -> TaskMeta:
        """
        Helper function to create the task metadata.

        Needs to be called to instantiate a task
        """
        task_info = TaskMeta(
            name=self.name,
            source=self.task_data_source,
            columns=self.table_schema.columns,
            time_column=self.time_column,
            task_type=self.task_type,
            evaluation_metric=self.evaluation_metric,
            target_column=self.target_entity_column,
            target_table=self.target_entity_table,
            source_column=self.source_entity_column,
            source_table=self.source_entity_table,
            current_time=self.current_time,
        )
        return task_info

    def show_task(self):
        """Display formatted information about the current task."""
        print("Task Information")
        print("=" * 50)
        print(f"Task name:      {self.name}")
        print(f"Task type:      {self.task_type.value}")

        print("\nTask Table Sources:")
        print("-" * 50)
        for key, val in self.task_data_source.items():
            print(f"  • {key}: {val}")
        print("\nEntity Information:")
        print("-" * 50)
        print(f"  • Target entity column: {self.target_entity_column}")
        print(f"  • Target entity table:  {self.target_entity_table}")
        print(f"  • Source entity column: {self.source_entity_column}")
        print(f"  • Source entity table:  {self.source_entity_table}")

        print("\nTime Information:")
        print("-" * 50)
        print(f"  • Time column: {self.time_column}")

        print("\nEvaluation:")
        print("-" * 50)
        print(f"  • Metric: {self.evaluation_metric}")

        print("\nTable Schema:")
        print("-" * 50)
        self.table_schema.table_info


class NodeTask(Task):
    """
    Class representing a node task.

    It can be node binary/multi-label/multi-class classification, or node regression
    """

    # If we specify time in task it shoudl have a field in thee database
    def __init__(
        self,
        connector: BaseConnector,
        name: str,
        task_data_source: Dict[Literal["train", "test", "validation"], str],
        source_entity_column: str,
        source_entity_table: str,
        target_column: str,
        task_type: Literal[
            TaskType.BINARY_CLASSIFICATION,
            TaskType.MULTICLASS_CLASSIFICATION,
            TaskType.MULTILABEL_CLASSIFICATION,
            TaskType.REGRESSION,
        ],
        time_column: Optional[str] = None,
        evaluation_metric: Optional[EvaluationMetric] = None,
        current_time: Optional[bool] = True,
    ):
        """
        Node task.

        :param connector: The connector object used for interacting with the data backend.
        :type connector: str

        :param name: The name of the task, which can describe the task at hand.
        :type name: str

        :param task_data_source: A dictionary with three keys: "train", "test", and "validation",
            each pointing to the path of the respective dataset. The path can be a `.csv` or `.parquet` file,
            or the name of a Snowflake table in the form `<Database.Schema.Table>`.
        :type task_data_source: Dict[Literal["train", "test", "validation"], str]

        :param source_entity_table: The name of the source entity table in link prediction tasks,
            or the name of the source entity table in node tasks.
        :type source_entity_table: str

        :param target_column: The name of the target column for node classification tasks.
            This column holds the values that will be used to train the model.
        :type target_column: str

        :param task: The type of the node task, which can be binary classification, multi-class classification,
            multi-label classification, or regression.
        :type task: Literal[TaskType.BINARY_CLASSIFICATION, TaskType.MULTICLASS_CLASSIFICATION,
            TaskType.MULTILABEL_CLASSIFICATION, TaskType.REGRESSION]

        :param time_column: Optional. The name of the time column. This can also be set later
            using the `set_time_column` function.
        :type time_column: Optional[str]

        :param evaluation_metric: Optional. The name of the evaluation metric to optimize for.
        :type evaluation_metric: Optional[EvaluationMetric]

        :param current_time: Optional. If set to False the current time of the task table will be reduced
                    by one time unit. Useful when the time column at the task table does not need to see the
                    values from the database tables at the same time stamp
        :type current_time: Optional[bool]
        """

        super().__init__(
            connector=connector,
            name=name,
            task_data_source=task_data_source,
            task_type=task_type,
            time_column=time_column,
            target_column=target_column,
            source_entity_column=source_entity_column,  # THIS IS THE SAME AS THE PRIMARY KEY
            source_entity_table=source_entity_table,
            evaluation_metric=evaluation_metric,
            current_time=current_time,
        )
        # initialize it calling the create_task function
        self.task_info = self._create_task()

    def _create_task(self) -> TaskMeta:
        """
        Helper function to create the task metadata.

        Needs to be called to instantiate a task
        """
        task_info = TaskMeta(
            name=self.name,
            source=self.task_data_source,
            columns=self.table_schema.columns,
            time_column=self.time_column,
            task_type=self.task_type,
            evaluation_metric=self.evaluation_metric,
            target_column=self.target_column,
            target_table=self.source_entity_table,
            current_time=self.current_time,
        )
        return task_info

    def show_task(self):
        """Display formatted information about the current task."""
        if self.task_info is None:
            print("Please create the dataset first")
            return

        print("Task Information")
        print("=" * 50)
        print(f"Task name:      {self.name}")
        print(f"Task type:      {self.task_type.value}")

        print("\nTask Table Sources:")
        print("-" * 50)
        for key, val in self.task_data_source.items():
            print(f" • {key}: {val}")
        print("\nColumn Information:")
        print("-" * 50)
        print(f"  • Target column:       {self.target_column}")
        print(f"  • Time column:          {self.time_column}")
        print(f"  • Source entity column: {self.source_entity_column}")
        print(f"  • Source entity table:  {self.source_entity_table}")

        print("\nEvaluation:")
        print("-" * 50)
        print(f"  • Metric: {self.evaluation_metric.name}")

        print("\nTable Schema:")
        print("-" * 50)
        self.table_schema.table_info

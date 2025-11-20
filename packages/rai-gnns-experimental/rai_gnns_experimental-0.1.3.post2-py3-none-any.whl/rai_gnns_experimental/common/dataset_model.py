from enum import Enum
from typing import Dict, List, Literal, Optional

import pydantic
from pydantic import Field, ValidationInfo, field_validator
from tabulate import tabulate

# --- Enums ---


class MetricName(str, Enum):
    """Metric names for all available metrics."""

    # binary classification
    AVERAGE_PRECISION = "average_precision"
    ACCURACY = "accuracy"  # also multi-class classification
    F1 = "f1"
    ROC_AUC = "roc_auc"
    # multilabel classification
    MULTILABEL_AUPRC_MICRO = "multilabel_auprc_micro"
    MULTILABEL_AUROC_MICRO = "multilabel_auroc_micro"
    MULTILABEL_PRECISION_MICRO = "multilabel_precision_micro"
    MULTILABEL_AUPRC_MACRO = "multilabel_auprc_macro"
    MULTILABEL_AUROC_MACRO = "multilabel_auroc_macro"
    MULTILABEL_PRECISION_MACRO = "multilabel_precision_macro"
    # multiclass classification
    MACRO_F1 = "macro_f1"
    MICRO_F1 = "micro_f1"
    # regerssion
    R2 = "r2"
    MAE = "mae"
    RMSE = "rmse"
    # all link prediction problems
    LINK_PREDICTION_PRECISION = "link_prediction_precision"
    LINK_PREDICTION_RECALL = "link_prediction_recall"
    LINK_PREDICTION_MAP = "link_prediction_map"


class TaskType(str, Enum):
    r"""The type of the tasks."""

    REGRESSION = "regression"
    BINARY_CLASSIFICATION = "binary_classification"
    MULTILABEL_CLASSIFICATION = "multilabel_classification"
    MULTICLASS_CLASSIFICATION = "multiclass_classification"
    REPEATED_LINK_PREDICTION = "repeated_link_prediction"
    LINK_PREDICTION = "link_prediction"


class TableDataFormat(str, Enum):
    """Table data formats."""

    PARQUET = "parquet"
    CSV = "csv"
    DUCKDB = "duckdb"
    SNOWFLAKE = "snowflake"
    RAI_LINK = "rai_link"


class ColumnDType(str, Enum):
    """Column data types."""

    float_t = "float"
    category_t = "category"
    datetime_t = "datetime"
    text_t = "text"
    embedding_t = "embedding"
    integer_t = "integer"
    multi_category_t = "multi_categorical"


class KeysType(str, Enum):
    """Keys types."""

    foreign_key = "foreign_key"
    primary_key = "primary_key"


class TableType(str, Enum):
    """Table types."""

    NODE = "node"
    EDGE = "edge"


# --- Consts ---
METRICS_REQUIRING_K = {
    MetricName.LINK_PREDICTION_MAP,
    MetricName.LINK_PREDICTION_PRECISION,
    MetricName.LINK_PREDICTION_RECALL,
}


# --- Helper classes ---
class TaskMetricMapping:
    """Mapping of TaskType to valid MetricName values."""

    TASK_TYPE_TO_METRICS: Dict[TaskType, List[MetricName]] = {
        TaskType.REGRESSION: [MetricName.RMSE, MetricName.MAE, MetricName.R2],
        TaskType.MULTILABEL_CLASSIFICATION: [
            MetricName.MULTILABEL_AUPRC_MACRO,
            MetricName.MULTILABEL_AUPRC_MICRO,
            MetricName.MULTILABEL_AUROC_MACRO,
            MetricName.MULTILABEL_AUROC_MICRO,
            MetricName.MULTILABEL_PRECISION_MACRO,
            MetricName.MULTILABEL_PRECISION_MICRO,
        ],
        TaskType.BINARY_CLASSIFICATION: [
            MetricName.F1,
            MetricName.ACCURACY,
            MetricName.ROC_AUC,
            MetricName.AVERAGE_PRECISION,
        ],
        TaskType.MULTICLASS_CLASSIFICATION: [MetricName.ACCURACY, MetricName.MICRO_F1, MetricName.MACRO_F1],
        TaskType.LINK_PREDICTION: [
            MetricName.LINK_PREDICTION_MAP,
            MetricName.LINK_PREDICTION_PRECISION,
            MetricName.LINK_PREDICTION_RECALL,
        ],
        TaskType.REPEATED_LINK_PREDICTION: [
            MetricName.LINK_PREDICTION_MAP,
            MetricName.LINK_PREDICTION_PRECISION,
            MetricName.LINK_PREDICTION_RECALL,
        ],
    }

    @classmethod
    def get_valid_metrics(cls, task_type: TaskType):
        """Retrieve a list of valid metrics for a task type."""
        return cls.TASK_TYPE_TO_METRICS[task_type]

    @classmethod
    def is_valid_metric(cls, task_type: TaskType, metric: MetricName) -> bool:
        """Check if a metric is valid for a task type."""
        return metric.value.lower() in cls.TASK_TYPE_TO_METRICS[task_type]


# --- Models ---


class ColumnSchema(pydantic.BaseModel):
    """Column schema model."""

    class Config:
        extra = "allow"
        use_enum_values = True

    name: str
    dtype: ColumnDType
    key_type: Optional[KeysType] = None
    format: Optional[str] = None
    link_to: Optional[str] = Field(None, pattern=r"^[a-zA-Z]\w*\.[a-zA-Z]\w*$")

    @field_validator("name", mode="before")
    @classmethod
    def convert_name_to_str(cls, value):
        """Support int column names in the .yaml."""
        return str(value)


class ConnectorConfig(pydantic.BaseModel):
    """Configuration model for a connector."""

    class Config:
        use_enum_values = True

    name: TableDataFormat
    dataset_name: str
    extra_fields: Optional[Dict[str, str]] = {}


class TableSchema(pydantic.BaseModel):
    """Table schema model."""

    class Config:
        use_enum_values = True

    name: str = Field(description="name of the table")
    source: str = Field(description="full path to the file or table")
    type: TableType
    columns: List[ColumnSchema]
    time_column: Optional[str] = None
    extra_fields: Optional[Dict[str, str]] = {}

    @property
    def column_dict(self) -> Dict[str, ColumnSchema]:
        """Convert list of columns to a dictionary with column names as keys."""
        return {col_schema.name: col_schema for col_schema in self.columns}

    @property
    def table_info(self) -> None:
        """Print formatted table schema information."""
        # Table header
        print(f"\nTable: {self.name}")
        print(f"Source: {self.source}")
        if self.time_column:
            print(f"Time Column: {self.time_column}")

        # Prepare column information
        headers = ["Column Name", "Data Type", "Key Type", "Format", "Link To"]
        rows = []

        for column in self.columns:
            rows.append(
                [
                    column.name,
                    column.dtype,
                    column.key_type if column.key_type else "",
                    column.format if column.format else "",
                    column.link_to if column.link_to else "",
                ]
            )

        # Print column information using tabulate
        print("\nColumns:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))


class EvaluationMetric(pydantic.BaseModel):
    """Class representing an evaluation metric."""

    # TODO: change name to type MetricName (avoid this now since there
    # might be streamlit related dependencies)
    name: str
    eval_at_k: Optional[int] = Field(default=None)

    @field_validator("eval_at_k", mode="before")
    @classmethod
    def validate_eval_at_k(cls, value, values: ValidationInfo):
        """Validate if eval_at_k is not None for link prediction metrics."""
        metric_name = MetricName(values.data.get("name"))
        # TODO: Revert to this once we change the name to not be str
        # metric_name = values.data.get("name")
        if metric_name in METRICS_REQUIRING_K and value is None:
            raise ValueError(f"❌ eval_at_k cannot be None for metric {metric_name.value}")
        return value


class TaskMeta(pydantic.BaseModel):
    """Task metadata model."""

    class Config:
        use_enum_values = True

    name: str
    source: Dict[Literal["train", "test", "validation"], Optional[str]]
    columns: List[ColumnSchema]
    time_column: Optional[str] = None
    target_column: str
    target_table: str
    current_time: Optional[bool] = True
    source_column: Optional[str] = None
    source_table: Optional[str] = None
    task_type: TaskType
    evaluation_metric: EvaluationMetric
    extra_fields: Optional[Dict[str, str]] = {}

    @field_validator("evaluation_metric")
    @classmethod
    def validate_metric_for_task(cls, value, values: ValidationInfo):
        """Check if the evaluation metric is valid for a task type."""
        # TODO: Here metric name will be of type STR because of
        # possible streamlit dependencies, switch to MetricName
        metric_name = value.name
        task_type = values.data.get("task_type")

        metric_name = MetricName(metric_name)
        if not TaskMetricMapping.is_valid_metric(TaskType(task_type), metric_name):
            raise ValueError(f"Metric {metric_name.name} is not valid for {task_type}")
        return value

    @property
    def column_dict(self) -> Dict[str, ColumnSchema]:
        """Convert list of columns to a dictionary with column names as keys."""
        return {col_schema.name: col_schema for col_schema in self.columns}

    @property
    def task_summary(self) -> None:
        """Print a summary of the task configuration."""
        print(f"\nTask: {self.name}")
        print(f"Type: {self.task_type}")
        print(f"Target: {self.target_column} (in {self.target_table})")
        print(f"Evaluation Metric: {self.evaluation_metric}")
        # Prepare column information
        headers = ["Column Name", "Data Type", "Key Type", "Format", "Link To"]
        rows = []

        for column in self.columns:
            rows.append(
                [
                    column.name,
                    column.dtype,
                    column.key_type if column.key_type else "",
                    column.format if column.format else "",
                    column.link_to if column.link_to else "",
                ]
            )

        # Print column information using tabulate
        print("\nTraining Columns:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))


class DatasetMeta(pydantic.BaseModel):
    """Dataset metadata model."""

    # Connector type.
    connector: ConnectorConfig
    # Table schemas.
    tables: List[TableSchema]
    # Task metadata.
    task: TaskMeta

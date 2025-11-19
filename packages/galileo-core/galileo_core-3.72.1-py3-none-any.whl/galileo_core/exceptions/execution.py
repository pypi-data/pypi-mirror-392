from typing import Optional

from galileo_core.exceptions.base import BaseGalileoException


class ExecutionError(BaseGalileoException):
    """Raised when there is an issue with the execution of a task or process."""

    ...


class MetricNotFoundError(ExecutionError):
    """Raised when attempting to access a metric that doesn't exist in the Metrics object."""

    def __init__(self, metric_name: str, extra: Optional[dict] = None):
        message = (
            f"Metric '{metric_name}' does not exist. "
            f"The metric you have attempted to retrieve is either not in the required metrics, "
            f"or you have used an incorrect name."
        )
        super().__init__(message, extra)

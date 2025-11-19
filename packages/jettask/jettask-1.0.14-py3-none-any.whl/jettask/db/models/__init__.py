"""
数据库模型定义

所有表的 SQLAlchemy 模型定义
"""

from .task import Task
from .task_run import TaskRun
from .scheduled_task import ScheduledTask, TaskExecutionHistory
from .task_metrics_minute import TaskMetricsMinute
from .task_runs_metrics_minute import TaskRunsMetricsMinute
from .sql_history import SQLHistory

from jettask.core.enums import TaskType, TaskStatus

__all__ = [
    'Task',
    'TaskRun',
    'ScheduledTask',
    'TaskExecutionHistory',
    'TaskMetricsMinute',
    'TaskRunsMetricsMinute',
    'SQLHistory',
    'TaskType',
    'TaskStatus',
]

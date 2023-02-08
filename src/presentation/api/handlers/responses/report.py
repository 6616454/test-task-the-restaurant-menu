from pydantic import BaseModel, Field

from src.domain.report.dto.report import ReportStatusTask


class ReportTaskResponse(BaseModel):
    task_id: str
    detail = Field("Task for get Excel-file for Menu started...", const=True)


class ReportTaskStatusResponse(BaseModel):
    task: ReportStatusTask
    detail: str = Field(
        "Wait when status of task will be SUCCESS and download file", const=True
    )

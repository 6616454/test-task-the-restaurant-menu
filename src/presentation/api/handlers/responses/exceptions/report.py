from pydantic import Field

from src.presentation.api.handlers.responses.base import ApiError


class ReportDataEmptyError(ApiError):
    detail = Field("Report data for create Excel-file with menu was empty", const=True)


class ReportFileNotFoundError(ApiError):
    detail = Field("Report file is not ready or not created", const=True)

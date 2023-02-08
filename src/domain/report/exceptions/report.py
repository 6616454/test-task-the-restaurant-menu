from src.domain.common.exceptions.base import AppException


class ReportException(AppException):
    """Base report exception"""

    pass


class ReportDataEmpty(ReportException):
    """Report data empty exception"""

    pass

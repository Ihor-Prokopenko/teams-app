from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict) -> Response:
    """A custom exception handler that handles exceptions raised during the execution of the API view."""
    response = exception_handler(exc, context)
    if isinstance(exc, PermissionDenied):
        response.data = {"message": exc.detail}
    return response


class RetryExceptionError(Exception):
    """ Custom exception that handles exceptions raised during the execution of the API view. """

    def __init__(self, message: str, status: int) -> None:

        self.message = message
        self.status = status


class RetryExceptionHandler:
    """ Custom exception handler that handles exceptions raised during the execution of the API view. """

    def handle_exception(self, exception: Exception) -> Response:
        """ Handle exceptions raised during the execution of the API view. """
        if isinstance(exception, RetryExceptionError):
            return Response({'message': exception.message}, status=exception.status)
        response = exception_handler(exception, self)
        return response

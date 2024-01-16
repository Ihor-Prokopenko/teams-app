from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class RetryExceptionError(Exception):
    """ Custom exception that handles exceptions raised during the execution of the API view. """
    def __init__(self, message: str, status: int) -> None:

        self.message = message
        self.status = status


class RetryExceptionHandlerMixin:
    """ Custom exception handler that handles exceptions raised during the execution of the API view. """

    def handle_exception(self, exception: Exception) -> Response:
        """ Handle exceptions raised during the execution of the API view. """
        if isinstance(exception, RetryExceptionError):
            return Response({'message': exception.message}, status=exception.status)
        if isinstance(exception, DatabaseError):
            return Response({'message': str(exception)}, status=status.HTTP_417_EXPECTATION_FAILED)
        response = exception_handler(exception, self)
        return response

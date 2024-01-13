from rest_framework.response import Response
from rest_framework.views import exception_handler


class RetryExceptionError(Exception):

    def __init__(self, message: str, status):

        self.message = message
        self.status = status


class RetryExceptionHandler:

    def handle_exception(self, exception):
        response = exception_handler(exception, self)
        if isinstance(exception, RetryExceptionError):
            return Response({'message': exception.message}, status=exception.status)
        return response

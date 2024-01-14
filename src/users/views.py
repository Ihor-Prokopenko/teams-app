from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from base.exception_handlers import RetryExceptionHandler, RetryExceptionError
from .serializers import UserSerializer, LoginSerializer
from .models import User

from retrying import retry


class UserCreateAPIView(RetryExceptionHandler, CreateAPIView):
    """Create a new user."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [~permissions.IsAuthenticated]

    @retry(stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS, wait_fixed=settings.RETRY_WAIT_FIXED)
    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create a new user."""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        else:
            validated_data = serializer.validated_data
            password = validated_data.get('password')
            hashed_password = make_password(password)
            validated_data['password'] = hashed_password
            success = serializer.save()
            if not success:
                raise RetryExceptionError('User creation failed', status.HTTP_417_EXPECTATION_FAILED)

            message = 'New user created'
            status_code = status.HTTP_201_CREATED

        return Response({'message': message}, status=status_code)


class UserLoginAPIView(CreateAPIView):
    """Log in a user."""

    serializer_class = LoginSerializer
    permission_classes = [~permissions.IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Log in a user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            response_data = {'message': 'Invalid Credentials'}
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            response_data = {'message': 'Invalid Credentials'}
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)

        login(request, user)

        response_data = {'message': 'Login Successful'}

        return Response(response_data, status=status.HTTP_200_OK)


class UserLogoutAPIView(APIView):
    """ Log out a user. """

    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def post(request: Request) -> Response:
        """ Log out a user."""
        logout(request)
        response_data = {'message': 'Logged out successfully'}
        response = Response(response_data, status=status.HTTP_200_OK)
        return response

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.db import DatabaseError
from rest_framework import status, permissions, filters, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from base.exception_handlers import RetryExceptionHandlerMixin, RetryExceptionError
from base.mixins import ListMixin
from .permissions import DeleteUserPermission
from .serializers import UserSerializer, LoginSerializer, UserEditSerializer, ChangePasswordSerializer
from .models import User

from retrying import retry


""" USER CRUD API ENDPOINTS """


class UserCreateAPIView(RetryExceptionHandlerMixin, CreateAPIView):
    """Create a new user."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [~permissions.IsAuthenticated]

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create a new user."""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            password = validated_data.get('password')
            hashed_password = make_password(password)
            validated_data['password'] = hashed_password
            serializer.save()

            message = 'New user created'
            status_code = status.HTTP_201_CREATED
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        return Response({'message': message}, status=status_code)


class UserListAPIView(RetryExceptionHandlerMixin, ListMixin, ListAPIView):
    """List all users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = '__all__'
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class UserEditView(RetryExceptionHandlerMixin, mixins.UpdateModelMixin, GenericAPIView):
    """Update user details. """

    queryset = User.objects.all()
    serializer_class = UserEditSerializer
    permission_classes = [permissions.IsAuthenticated]

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def put(self, request, *args, **kwargs) -> Response:
        """Update user details. """
        partial = True
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            message = 'User details updated'
            status_code = status.HTTP_200_OK
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
        return Response({"message": message}, status=status_code)


class DeleteUserAPIView(RetryExceptionHandlerMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, DeleteUserPermission]
    http_method_names = ["delete"]

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def delete(self, request: Request, pk) -> Response:
        """Delete a user."""
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        deleted_count, data = user.delete()
        if not deleted_count:
            return Response({'message': 'User deletion failed'}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response({'message': f'User(id={pk}) was deleted successfully'}, status=status.HTTP_200_OK)


class UserChangePasswordView(RetryExceptionHandlerMixin, mixins.UpdateModelMixin, GenericAPIView):
    """ Change user password. """

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def put(self, request, *args, **kwargs) -> Response:
        """Change user password. """
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_412_PRECONDITION_FAILED)

        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')
        confirm_password = serializer.validated_data.get('confirm_password')

        if new_password == old_password:
            return Response(
                {'message': 'New password must be different from old password'},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        if not check_password(old_password, user.password):
            return Response({'message': 'Invalid old password'}, status=status.HTTP_412_PRECONDITION_FAILED)

        if new_password != confirm_password:
            return Response({'message': 'Password mismatch'}, status=status.HTTP_412_PRECONDITION_FAILED)

        user.set_password(new_password)
        user.save()

        logout(request)
        response = Response({'message': 'Password changed successfully. You can login now.'}, status=status.HTTP_200_OK)

        return response


""" AUTH API ENDPOINTS """


class UserLoginAPIView(RetryExceptionHandlerMixin, CreateAPIView):
    """Log in a user."""

    serializer_class = LoginSerializer
    permission_classes = [~permissions.IsAuthenticated]

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
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
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        return Response({'message': 'Login Successful'}, status=status.HTTP_200_OK)


class UserLogoutAPIView(RetryExceptionHandlerMixin, APIView):
    """ Log out a user. """

    permission_classes = [permissions.IsAuthenticated]

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def post(self, request: Request) -> Response:
        """ Log out a user."""
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

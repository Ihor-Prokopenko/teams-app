from django.db import DatabaseError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, permissions, filters
from django.conf import settings

from .mixins import ListMixin
from .models import Team, Member
from .serializers import TeamSerializer, TeamCreateSerializer, MemberCreateSerializer, MemberSerializer, \
    MemberUpdateSerializer, TeamUpdateSerializer
from base.exception_handlers import RetryExceptionError, RetryExceptionHandler

from retrying import retry


""" TEAM API ENDPOINTS """


class TeamCreateAPIView(CreateAPIView):
    """ Create a new team """

    queryset = Team.objects.all()
    serializer_class = TeamCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ['POST']

    def create(self, request: Request, *args, **kwargs) -> Response:
        """ Create a new team """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        self.perform_create(serializer)
        return Response({'message': f'Team {serializer.data.get("name")} created'}, status=status.HTTP_201_CREATED)


class TeamListAPIView(ListMixin, ListAPIView):
    """ List all teams """

    serializer_class = TeamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = '__all__'
    allowed_methods = ['GET']

    def list(self, request: Request, *args, **kwargs) -> Response:
        """ List of all user's teams """
        self.queryset = request.user.teams.all()
        return super().list(request, *args, **kwargs)


class TeamDetailAPIView(RetrieveAPIView):
    """ Get details of a team """
    serializer_class = TeamSerializer
    lookup_field = 'pk'
    allowed_methods = ['GET']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> list[Team]:
        queryset = self.request.user.teams.all().prefetch_related('members')
        self.queryset = queryset
        return queryset


class TeamUpdateAPIView(RetryExceptionHandler, UpdateAPIView):
    """ Update details of a team """

    serializer_class = TeamUpdateSerializer
    lookup_field = 'pk'
    allowed_methods = ['PUT']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> list[Team]:
        queryset = self.request.user.teams.all()
        self.queryset = queryset
        return queryset

    @retry(stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS, wait_fixed=settings.RETRY_WAIT_FIXED)
    def put(self, request: Request, *args, **kwargs) -> Response:
        """ Update details of a team """
        partial = True
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                self.perform_update(serializer)
            except Exception as error:
                raise RetryExceptionError(str(error), status.HTTP_417_EXPECTATION_FAILED)

            message = 'Team details updated'
            status_code = status.HTTP_200_OK

        return Response({'message': message}, status=status_code)


class TeamDeleteAPIView(RetryExceptionHandler, DestroyAPIView):
    """ Delete a team """

    serializer_class = TeamSerializer
    lookup_field = 'pk'
    allowed_methods = ['DELETE']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> list[Team]:
        queryset = self.request.user.teams.all()
        self.queryset = queryset
        return queryset

    @retry(stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS, wait_fixed=settings.RETRY_WAIT_FIXED)
    def delete(self, request: Request, *args, **kwargs) -> Response:
        """ Delete a team """
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except DatabaseError as error:
            raise RetryExceptionError(str(error), status.HTTP_417_EXPECTATION_FAILED)
        return Response({'message': 'Team deleted'}, status=status.HTTP_200_OK)


"""  MEMBER API ENDPOINTS """


class MemberCreateView(CreateAPIView):
    """ Create a new member """

    queryset = Member.objects.all()
    serializer_class = MemberCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ['POST']

    def create(self, request: Request, *args, **kwargs) -> Response:
        """ Create a new member """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        try:
            self.perform_create(serializer)
        except DatabaseError as error:
            raise RetryExceptionError(str(error), status.HTTP_417_EXPECTATION_FAILED)

        full_name = serializer.data.get('full_name')
        email = serializer.data.get('email')
        return Response({'message': f'Member {full_name} ({email}) created'}, status=status.HTTP_201_CREATED)


class MemberListAPIView(ListMixin, ListAPIView):
    """ List all members """

    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = '__all__'
    allowed_methods = ['GET']

    def list(self, request: Request, *args, **kwargs) -> Response:
        """ List of all user's members """
        self.queryset = request.user.members.all()
        return super().list(request, *args, **kwargs)


class MemberDetailAPIView(RetrieveAPIView):
    """ Get details of a member """

    serializer_class = MemberSerializer
    lookup_field = 'pk'
    allowed_methods = ['GET']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> list[Member]:
        queryset = self.request.user.members.all().prefetch_related('team')
        self.queryset = queryset
        return queryset


class MemberUpdateAPIView(RetryExceptionHandler, UpdateAPIView):
    """ Update user details """

    serializer_class = MemberUpdateSerializer
    lookup_field = 'pk'
    allowed_methods = ['PUT']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> list[Member]:
        queryset = self.request.user.members.all()
        self.queryset = queryset
        return queryset

    @retry(stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS, wait_fixed=settings.RETRY_WAIT_FIXED)
    def put(self, request: Request, *args, **kwargs) -> Response:
        """Update member details"""
        partial = True
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                self.perform_update(serializer)
            except DatabaseError as error:
                raise RetryExceptionError(str(error), status.HTTP_417_EXPECTATION_FAILED)

            message = 'Member details updated'
            status_code = status.HTTP_200_OK

        return Response({'message': message}, status=status_code)


class MemberDeleteAPIView(RetryExceptionHandler, DestroyAPIView):
    """ Delete a member """

    serializer_class = MemberSerializer
    lookup_field = 'pk'
    allowed_methods = ['DELETE']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> list[Member]:
        queryset = self.request.user.members.all()
        self.queryset = queryset
        return super().get_queryset()

    @retry(stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS, wait_fixed=settings.RETRY_WAIT_FIXED)
    def delete(self, request: Request, *args, **kwargs) -> Response:
        """ Delete a member """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except DatabaseError as error:
            raise RetryExceptionError(str(error), status.HTTP_417_EXPECTATION_FAILED)
        return Response({'message': 'Member deleted'}, status=status.HTTP_200_OK)

from django.db import DatabaseError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, permissions, filters, mixins
from django.conf import settings

from base.mixins import ListMixin
from .models import Team, Member
from .serializers import TeamSerializer, TeamCreateSerializer, MemberCreateSerializer, MemberSerializer, \
    MemberUpdateSerializer, TeamUpdateSerializer
from base.exception_handlers import RetryExceptionHandlerMixin

from retrying import retry


""" TEAM API ENDPOINTS """


class TeamCreateAPIView(RetryExceptionHandlerMixin, CreateAPIView):
    """ Create a new team """

    queryset = Team.objects.all()
    serializer_class = TeamCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ['POST']

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        """ Create a new team """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
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


class TeamUpdateAPIView(RetryExceptionHandlerMixin, mixins.UpdateModelMixin, GenericAPIView):
    """Update team details. """

    queryset = Team.objects.all()
    serializer_class = TeamUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def put(self, request, pk: int) -> Response:
        """Update team details. """
        partial = True
        team = request.user.teams.filter(pk=pk).first()
        serializer = self.get_serializer(team, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            message = 'Team details updated'
            status_code = status.HTTP_200_OK
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
        return Response({"message": message}, status=status_code)


class TeamDeleteAPIView(RetryExceptionHandlerMixin, DestroyAPIView):
    """ Delete a team """

    serializer_class = TeamSerializer
    lookup_field = 'pk'
    allowed_methods = ['DELETE']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> list[Team]:
        queryset = self.request.user.teams.all()
        self.queryset = queryset
        return queryset

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        """ Delete a team """
        instance = self.get_object()
        if not instance:
            return Response({'message': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response({'message': 'Team deleted'}, status=status.HTTP_200_OK)


"""  MEMBER API ENDPOINTS """


class MemberCreateAPIView(RetryExceptionHandlerMixin, CreateAPIView):
    """ Create a new member """

    queryset = Member.objects.all()
    serializer_class = MemberCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ['POST']

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        """ Create a new member """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
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


class MemberUpdateAPIView(RetryExceptionHandlerMixin, mixins.UpdateModelMixin, GenericAPIView):
    """Update user details. """

    queryset = Member.objects.all()
    serializer_class = MemberUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def put(self, request, pk: int) -> Response:
        """Update user details. """
        partial = True
        member = request.user.members.filter(pk=pk).first()
        serializer = self.get_serializer(member, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            message = 'Member details updated'
            status_code = status.HTTP_200_OK
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
        return Response({"message": message}, status=status_code)


class MemberDeleteAPIView(RetryExceptionHandlerMixin, DestroyAPIView):
    """ Delete a member """

    serializer_class = MemberSerializer
    lookup_field = 'pk'
    allowed_methods = ['DELETE']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> list[Member]:
        queryset = self.request.user.members.all()
        self.queryset = queryset
        return super().get_queryset()

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        """ Delete a member """
        instance = self.get_object()
        if not instance:
            return Response({'message': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response({'message': 'Member deleted'}, status=status.HTTP_200_OK)


""" MANAGER API ENDPOINTS """


class AddMemberAPIView(APIView):
    """ Add a member to a team """

    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ['POST']

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """ Add a member to a team """
        team = request.user.teams.all().filter(pk=kwargs.get('team_pk')).first()
        member = request.user.members.all().filter(pk=kwargs.get('member_pk')).first()
        if not team or not member:
            message = 'Invalid team or member'
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        if member.team == team:
            message = 'Member already in the team'
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        member.team = team
        member.save()
        return Response({'message': 'Member added to the team'}, status=status.HTTP_200_OK)


class RemoveMemberAPIView(APIView):
    """ Remove a member from a team """

    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ['POST']

    @retry(
        stop_max_attempt_number=settings.RETRY_MAX_ATTEMPTS,
        wait_fixed=settings.RETRY_WAIT_FIXED,
        retry_on_exception=lambda ex: isinstance(ex, DatabaseError),
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """ Remove a member from a team """
        team = request.user.teams.all().filter(pk=kwargs.get('team_pk')).first()
        member = request.user.members.all().filter(pk=kwargs.get('member_pk')).first()
        if not team or not member:
            message = 'Invalid team or member'
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        if member.team != team:
            message = 'Member is not in the team'
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        member.team = None
        member.save()
        return Response({'message': 'Member removed from the team'}, status=status.HTTP_200_OK)

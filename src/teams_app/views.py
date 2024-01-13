from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, permissions, filters

from .mixins import ListMixin
from .models import Team, Member
from .serializers import TeamSerializer, TeamCreateSerializer, MemberCreateSerializer, MemberSerializer


class TeamCreateAPIView(CreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
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
    serializer_class = TeamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = "__all__"

    def list(self: Request, request, *args, **kwargs):
        self.queryset = request.user.teams.all()
        return super().list(request, *args, **kwargs)


class MemberCreateView(CreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            message = error.detail
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({'message': message}, status=status_code)
        self.perform_create(serializer)

        full_name = serializer.data.get('full_name')
        email = serializer.data.get('email')
        return Response({'message': f'Member {full_name} ({email}) created'}, status=status.HTTP_201_CREATED)


class MemberListAPIView(ListMixin, ListAPIView):
    serializer_class = MemberSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = "__all__"

    def list(self: Request, request, *args, **kwargs):
        self.queryset = request.user.members.all()
        return super().list(request, *args, **kwargs)

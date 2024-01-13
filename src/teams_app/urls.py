from django.urls import path, include

from teams_app import views


teams_crud = [
    path('', views.TeamListAPIView.as_view(), name="team-list"),
    path('create/', views.TeamCreateAPIView.as_view(), name="create-team"),
]

members_crud = [
    path('', views.MemberListAPIView.as_view(), name="member-list"),
    path('create/', views.MemberCreateView.as_view(), name="create-member"),
]


teams = [
    path('teams/', include(
        teams_crud,
    )),
]

members = [
    path('members/', include(
        members_crud,
    ))
]


urlpatterns = [] + teams + members

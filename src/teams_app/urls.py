from django.urls import path, include

from teams_app import views


teams_crud = [
    path('', views.TeamListAPIView.as_view(), name="team-list"),
    path('<int:pk>/', views.TeamDetailAPIView.as_view(), name="team-detail"),
    path('create/', views.TeamCreateAPIView.as_view(), name="team-create"),
    path('<int:pk>/update/', views.TeamUpdateAPIView.as_view(), name="team-update"),
    path('<int:pk>/delete/', views.TeamDeleteAPIView.as_view(), name="team-delete"),
]

members_crud = [
    path('', views.MemberListAPIView.as_view(), name="member-list"),
    path('<int:pk>/', views.MemberDetailAPIView.as_view(), name="member-detail"),
    path('create/', views.MemberCreateView.as_view(), name="member-create"),
    path('<int:pk>/update/', views.MemberUpdateAPIView.as_view(), name="member-update"),
    path('<int:pk>/delete/', views.MemberDeleteAPIView.as_view(), name="member-delete"),
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

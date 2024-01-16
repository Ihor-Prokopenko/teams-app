from django.urls import path, include

from teams_app import views


teams_crud = [
    path('', views.TeamListAPIView.as_view(), name="team_list"),
    path('<int:pk>/', views.TeamDetailAPIView.as_view(), name="team_detail"),
    path('create/', views.TeamCreateAPIView.as_view(), name="team_create"),
    path('update/<int:pk>/', views.TeamUpdateAPIView.as_view(), name="team_update"),
    path('delete/<int:pk>/', views.TeamDeleteAPIView.as_view(), name="team_delete"),
]

members_crud = [
    path('', views.MemberListAPIView.as_view(), name="member_list"),
    path('<int:pk>/', views.MemberDetailAPIView.as_view(), name="member_detail"),
    path('create/', views.MemberCreateAPIView.as_view(), name="member_create"),
    path('update/<int:pk>/', views.MemberUpdateAPIView.as_view(), name="member_update"),
    path('delete/<int:pk>/', views.MemberDeleteAPIView.as_view(), name="member_delete"),
]

teams_management = [
    path('<int:team_pk>/add-member/<int:member_pk>/', views.AddMemberAPIView.as_view(), name="add_member"),
    path('<int:team_pk>/remove-member/<int:member_pk>/', views.RemoveMemberAPIView.as_view(), name="remove_member"),
]

teams = [
    path('teams/', include([
        *teams_crud,
        *teams_management,
    ])),
]

members = [
    path('members/', include([
        *members_crud,
    ]))
]

urlpatterns = [] + teams + members

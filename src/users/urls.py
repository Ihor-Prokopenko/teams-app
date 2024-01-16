from django.urls import path

from users import views


crud = [
    path('', views.UserListAPIView.as_view(), name='user_list'),
    path('register/', views.UserCreateAPIView.as_view(), name='register'),
    path("edit-profile/", views.UserEditView.as_view(), name='edit_profile'),
    path("change-password/", views.UserChangePasswordView.as_view(), name='change_password'),
    path("delete/<int:pk>/", views.DeleteUserAPIView.as_view(), name='delete_user'),
]

auth = [
    path('login/', views.UserLoginAPIView.as_view(), name='login'),
    path('logout/', views.UserLogoutAPIView.as_view(), name='logout'),
]

urlpatterns = [] + crud + auth

from django.urls import path

from users import views


crud = [
    path('register/', views.UserCreateAPIView.as_view(), name="register"),
]

auth = [
    path('login/', views.UserLoginAPIView.as_view(), name="login"),
    path('logout/', views.UserLogoutAPIView.as_view(), name="logout"),
]

urlpatterns = [] + crud + auth

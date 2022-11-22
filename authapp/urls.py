from django.urls import path
from authapp.views import UserLogin, UserRegister, UserLogout, UserPasswordChange, UserChangeDone, UserChangePic


urlpatterns = [
    path('login/', UserLogin.as_view(), name='login'),
    path('register/', UserRegister.as_view(), name='user_register'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('change-pic/<int:id>/', UserChangePic.as_view(), name='change_pic'),
    path('change-password/<int:id>/', UserPasswordChange.as_view(), name='change_password'),
    path('change-password-done/',  UserChangeDone.as_view(), name='change_done'),
    ]

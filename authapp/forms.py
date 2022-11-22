from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from authapp.models import User


class UserRegister(UserCreationForm): 

    class Meta:
        model = User
        fields = ('username', 'email',)


class UserPasswordChange(PasswordChangeForm):
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Подтвердите новый пароль ещё раз', widget=forms.PasswordInput)
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput)     

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2',)

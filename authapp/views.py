from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.views.generic.edit import UpdateView

from authapp.forms import UserRegister, UserPasswordChange
from mainapp.forms import ImageUploadForm
from authapp.models import User


class UserLogin(LoginView):
    model = User
    template_name = 'login.html'


class UserLogout(LogoutView):
    model = User
    template_name = 'logout.html'


class UserRegister(CreateView):
    model = User
    form_class = UserRegister
    template_name = 'register.html'

    def get_context_data(self, **kwargs):
        """Отображает форму загрузки изображения"""
        context = super().get_context_data(**kwargs)
        context["img_form"] = ImageUploadForm
        return context

    def post(self, request):
        """1)Проверяет наличие имени пользователя и email в базе. Если такого пользователя нет, то создаёт его.
           2)Создает пользователя вне зависимости загружено ли изображение."""
        form = self.form_class(request.POST)
        img_form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            if img_form.is_valid():
                img_of_user = img_form.save()
                img_of_user.save()
                user_reg = form.save(commit=False)
                user_reg.save()
                user_reg.userpic.add(img_of_user)
            else:
                return render(request, self.template_name, {'form': form, "img_form": ImageUploadForm,
                              'error_message': 'Не удалось загрузить изображение'})
        else:
            username_res = User.objects.filter(username=self.request.POST.get("username"))
            email_res = User.objects.filter(email=self.request.POST.get("email"))
            if username_res:
                error_message = 'Пользователь с данным именем уже зарегистрирован'
            elif email_res:
                error_message = 'Пользователь с данным email уже зарегистрирован'
            else:
                error_message = 'Ошибка регистрации'
            return render(request, self.template_name, {'form': form, "img_form": ImageUploadForm,
                          'error_message': error_message})
        return HttpResponseRedirect(reverse_lazy('login'))


class UserPasswordChange(PasswordChangeView):
    model = User
    form_class = UserPasswordChange
    template_name = 'change_password.html'
    success_url = reverse_lazy('change_done')


class UserChangeDone(PasswordChangeDoneView):
    template_name = 'success.html'


class UserChangePic(UpdateView):
    model = User
    form_class = ImageUploadForm
    template_name = 'change_pic.html'

    def get_context_data(self, *args, **kwargs):
        """Отображает форму"""
        if self.request.user.id != self.object.id:
            context = {'error_message': 'Редактировать можно только свой профиль ;)'}
        else:     
            context = super().get_context_data(*args, **kwargs)
            context["form"] = ImageUploadForm
        return context

    def get_object(self):
        obj = self.model.objects.get(id=self.kwargs['id'])
        return obj 

    def post(self, request, *args, **kwargs):
        """
        Заменяет аватарку пользователя, если в форму загружено изображение.
        Если изображение не загружено то оставляет прежнее изображение.
        """
        img_form = ImageUploadForm(request.POST, request.FILES)
        self.object = self.get_object()
        if img_form.is_valid() and \
                (img_form.cleaned_data.get('original') is not None or img_form.cleaned_data['image_url'] is not None):
            img_of_user = img_form.save()
            img_of_user.save()
            if img_of_user.original is not None:
                self.object.userpic.clear()
                self.object.userpic.add(img_of_user)
            self.object.save()
            context = {'form': img_form, 'error_message': 'Изменения успешно сохранены'}
            return render(request, self.template_name, context)
        elif img_form.is_valid() and \
                (img_form.cleaned_data.get('original') is None or img_form.cleaned_data['image_url'] is None):
            self.object.save()
            context = {'form': img_form, 'error_message': 'Изображение не было загружено'}
            return render(request, self.template_name, context)
        else:
            context = {'form': img_form, 'error_message': 'Не удалось загрузить изображение'}
            return render(request, self.template_name, context)

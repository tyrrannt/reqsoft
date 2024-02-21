import pyotp
import qrcode
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DetailView

from customeuser_app.forms import ProfileUpdateForm, UserUpdateForm, UserLoginForm, UserPasswordChangeForm, OTPUserForm
from customeuser_app.models import Profile
from customeuser_app.utils import return_secret_key, send_otp
from reqsoft.settings import MEDIA_URL, MEDIA_ROOT


# Create your views here.

class ProfileDetailView(DetailView):
    """
    Представление для просмотра профиля
    """
    model = Profile
    queryset = model.objects.all().select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f' - Страница пользователя: {self.object.user.username}'
        return context


class ProfileUpdateView(UpdateView):
    """
    Представление для редактирования профиля
    """
    model = Profile
    form_class = ProfileUpdateForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f' - Редактирование профиля пользователя: {self.request.user.username}'
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('customeuser_app:profile_detail', kwargs={'pk': self.object.pk})


class UserLoginView(SuccessMessageMixin, LoginView):
    """
    Авторизация на сайте
    """
    form_class = UserLoginForm
    template_name = 'customeuser_app/user_login.html'
    next_page = 'blog_app:article_list'
    success_message = 'Добро пожаловать на сайт!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = ' - Авторизация на сайте'
        return context

    def form_valid(self, form):
        user = form.get_user()
        profile = get_object_or_404(Profile, user=user)
        if profile.otp:
            self.request.session['username'] = user.username
            send_otp(self.request)
            return redirect('customeuser_app:otp')
        else:
            auth.login(self.request, form.get_user())
            portal_session = 3600
            self.request.session.set_expiry(portal_session)
            return HttpResponseRedirect(self.get_success_url())


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """
    Изменение пароля пользователя
    """
    form_class = UserPasswordChangeForm
    template_name = 'customeuser_app/user_password_change.html'
    success_message = 'Ваш пароль был успешно изменён!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = ' - Изменение пароля на сайте'
        return context

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'pk': self.request.user.pk})


class UserLogoutView(SuccessMessageMixin, LogoutView):
    """
    Выход из аккаунта
    """
    next_page = 'blog_app:article_list'
    success_message = 'Вы вышли из аккаунта!'


def otp_compare(request):
    error_message = None
    if request.method == 'POST':
        otp = request.POST['otp']
        username = request.session['username']
        otp_secret_key = request.session['otp_secret_key']
        if otp_secret_key is not None:
            totp = pyotp.TOTP(otp_secret_key)
            if totp.verify(otp):
                user_obj = get_object_or_404(User, username=username)
                auth.login(request, user_obj)
                del request.session['otp_secret_key']
                return HttpResponseRedirect(reverse_lazy('customeuser_app:profile_detail', args=(user_obj.pk,)))
            else:
                pass
        else:
            pass
    else:
        pass
    return render(request, 'customeuser_app/otp.html')


class OTPUser(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = OTPUserForm
    template_name = 'customeuser_app/otp_active.html'

    def get_context_data(self, **kwargs):
        context = super(OTPUser, self).get_context_data(**kwargs)
        user_obj = self.get_object()
        key = return_secret_key(user_obj.user)
        uri = pyotp.totp.TOTP(key).provisioning_uri(name=str(user_obj.user), issuer_name='REQSOFT_App')
        print()
        qrcode.make(uri).save(f'{MEDIA_ROOT}/{key}.png')
        context['qrcode'] = f'{MEDIA_URL}{key}.png'
        return context

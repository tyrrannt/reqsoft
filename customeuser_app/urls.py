from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import ProfileUpdateView, ProfileDetailView, UserLoginView, UserLogoutView, UserPasswordChangeView, \
    otp_compare, OTPUser

app_name = 'customeuser_app'

urlpatterns = [
    path('user/<int:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('user/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('otp/', otp_compare, name='otp'),
    path('user/<int:pk>/otp/', OTPUser.as_view(), name='otp_active')
]

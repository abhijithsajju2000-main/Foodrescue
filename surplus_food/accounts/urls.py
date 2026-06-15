from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    
    path('login/', views.LoginView.as_view(), name='login'),
    
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
   
    path('generate-otp/', views.GenerateOTPView.as_view(), name='generate-otp'),
   
    path('set-password/', views.SetPasswordView.as_view(), name='set-password'),


]
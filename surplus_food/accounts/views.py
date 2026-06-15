from django.shortcuts import render, redirect

from django.views import View

from django.contrib.auth import authenticate, login, logout

from .models import Profile, RoleChoices

from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator

from django.contrib.auth.hashers import make_password

from django.utils import timezone

from surplus_food.utility import send_email, generate_otp

from .models import OTP

import threading

class RegisterView(View):

    template = 'accounts/register.html'

    page = 'Register'

    def get(self, request, *args, **kwargs):

        data = {'page': self.page}

        return render(request, self.template, context=data)

    def post(self, request, *args, **kwargs):

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        role = request.POST.get('role')
        
        ALLOWED_ROLES = ['User', 'NGO', 'Donor']
        
        if role not in ALLOWED_ROLES:
            
            role = 'User' 

        phone = request.POST.get('phone')

        address = request.POST.get('address')

        ngo_darpan_id = request.POST.get('ngo_darpan_id')

        organization_pan = request.POST.get('organization_pan')

        user = Profile.objects.create_user(

            username=username,

            email=email,

            password=password,

            role=role,

            phone=phone,

            address=address,
        )

        if role == RoleChoices.NGO:

            user.ngo_darpan_id = ngo_darpan_id

            user.organization_pan = organization_pan

            user.save()

        return redirect('login')


class LoginView(View):

    template = 'accounts/login.html'

    page = 'Login'

    def get(self, request, *args, **kwargs):

        data = {'page': self.page}

        return render(request, self.template, context=data)

    def post(self, request, *args, **kwargs):

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:

            login(request, user)

            if user.role == 'Admin':

                return redirect('admin-dashboard')

            elif user.role == 'Donor':

                return redirect('my-donations')

            else:

                return redirect('donation-list')

        data = {'page': self.page, 'error': 'Invalid credentials'}

        return render(request, self.template, context=data)


class LogoutView(View):

    def get(self, request, *args, **kwargs):

        logout(request)

        return redirect('login')
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfileView(View):

    template = 'accounts/profile.html'

    page = 'My Profile'

    def get(self, request, *args, **kwargs):
    
        data = {'page': self.page}
    
        return render(request, self.template, context=data)

    def post(self, request, *args, **kwargs):
    
        user = request.user
    
        user.phone = request.POST.get('phone')
    
        user.address = request.POST.get('address')
    
        user.save()
    
        return redirect('profile')
    
class ForgotPasswordView(View):

    template = 'accounts/forgot-password.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        if Profile.objects.filter(username=username).exists():
            request.session['reset_username'] = username
            return redirect('generate-otp')
        return render(request, self.template, {'error': 'Username not found'})


class GenerateOTPView(View):

    template = 'accounts/otp.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            username = request.session.get('reset_username')
            user = Profile.objects.get(username=username)

        otp = generate_otp()
        otp_obj, _ = OTP.objects.get_or_create(user=user)
        otp_obj.otp = otp
        otp_obj.otp_verified = False
        otp_obj.save()

        request.session['otp_time'] = timezone.now().timestamp()

        subject = 'FoodShare | OTP for Password Change'
        thread = threading.Thread(
            target=send_email,
            args=[subject, user.email, 'emails/otp-email.html', {'user': user, 'otp': otp}]
        )
        thread.start()

        return render(request, self.template, {'remaining_time': 300})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            username = request.session.get('reset_username')
            user = Profile.objects.get(username=username)

        user_otp = request.POST.get('otp')
        db_otp = user.otp.otp
        otp_time = request.session.get('otp_time')
        msg = None

        if otp_time:
            elapsed = timezone.now().timestamp() - otp_time
            if elapsed > 300:
                msg = 'OTP expired. Please request a new one.'
            elif user_otp == db_otp:
                user.otp.otp_verified = True
                user.otp.save()
                return redirect('set-password')
            else:
                msg = 'Invalid OTP'

        remaining_time = max(0, 300 - (elapsed if otp_time else 0))
        return render(request, self.template, {'msg': msg, 'remaining_time': remaining_time})


class SetPasswordView(View):

    template = 'accounts/set-password.html'

    def get(self, request, *args, **kwargs):
 
        if request.user.is_authenticated:
 
            user = request.user
 
        else:
 
            username = request.session.get('reset_username')
 
            user = Profile.objects.get(username=username)

        if user.otp.otp_verified:
 
            return render(request, self.template)
 
        return redirect('generate-otp')

    def post(self, request, *args, **kwargs):
 
        if request.user.is_authenticated:
 
            user = request.user
 
        else:
 
            username = request.session.get('reset_username')
 
            user = Profile.objects.get(username=username)

        password = request.POST.get('password')
 
        confirm = request.POST.get('confirm_password')

        if password != confirm:
 
            return render(request, self.template, {'error': 'Passwords do not match'})

        user.password = make_password(password)
 
        user.save()
 
        user.otp.otp_verified = False
 
        user.otp.save()
 
        request.session.clear()
 
        logout(request)
 
        return redirect('login')
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from .forms import RegistrationForm, UserUpdateForm


def send_confirm_email(user,subject,template_name):
    mail_subject = subject
    message = render_to_string(template_name, {
        'user': user,
    })
    send_email = EmailMessage(
        mail_subject,
        message,
        to=[user.email]
    )
    send_email.content_subtype = 'html'
    send_email.send()

# Create your views here.
class UserRegistrationView(FormView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Register'
        return context
    
    def form_valid(self, form):
        user=form.save()
        login(self.request, user)
        messages.success(self.request, 'Account created successfully')
        send_confirm_email(user, 'Welcome to Bank of Django', 'register_email.html')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.warning(self.request, 'Account creation failed')
        return super().form_invalid(form)
    
class UserLoginView(LoginView):
    template_name = 'Login.html'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Login'
        return context
    
    def form_valid(self, form):
        user=form.get_user()
        login(self.request, user)
        messages.success(self.request, 'Login successful')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.warning(self.request, 'Login failed')
        return super().form_invalid(form)
    

def user_logout(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('home')
   
class UserProfileUpdateView(LoginRequiredMixin,View):
    template_name = 'profile.html'
    
    def get(self,request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self,request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        messages.warning(request, 'Profile update failed')
        return render(request, self.template_name, {'form': form})

class UserPasswordChangeView(LoginRequiredMixin,PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully')
        send_confirm_email(self.request.user, 'Password Change Confirmation', 'change_password_email.html')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.warning(self.request, 'Password change failed')
        return super().form_invalid(form)    
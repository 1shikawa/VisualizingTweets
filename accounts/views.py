from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from .forms import SignUpForm, LoginForm


# Create your views here.

class SignUp(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            # user = authenticate(email=email, password=raw_password)
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return redirect('VisualizingTweets:Index')
        return render(request, 'signup.html', {'form': form})


class Login(LoginView):
    form_class = LoginForm
    template_name = 'login.html'


# class Logout(LogoutView):
#     template_name = 'logout.html'

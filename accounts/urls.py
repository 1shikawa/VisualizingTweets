from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # path('signup/', views.SignUp.as_view(), name='signup'),
    path('guestlogin/', views.DefaultUserLogin.as_view(), name='default_user_login'),
    # path('logout/', views.Logout.as_view(), name='logout'),
]

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('guestlogin/', views.GuestLogin, name='guest_login'),
    # path('signup/', views.SignUp.as_view(), name='signup'),
    # path('logout/', views.Logout.as_view(), name='logout'),
]

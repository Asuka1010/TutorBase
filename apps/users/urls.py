from django.urls import path, include

from apps.users import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Account Related URLS
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/profile/', user_views.ProfileView.as_view(), name='profile'),
    path('accounts/profile/edit/', user_views.UserProfileUpdateView.as_view(), name='profile_edit'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

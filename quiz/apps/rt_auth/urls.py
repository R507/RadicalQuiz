"""Custom auth app urls"""
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    url('^login/$',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'),
    url('^logout/$',
        auth_views.LogoutView.as_view(template_name='registration/logout.html'),
        name='logout'),
    url(r'^', include('registration.backends.simple.urls')),
]

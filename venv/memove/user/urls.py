from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url

urlpatterns = [
    path('', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'), name='alogout'),
    path('user_update/', views.user_update, name='user_update'),
    path('profile/', views.profile_view, name='profile'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        views.activate, name='activate'),
]

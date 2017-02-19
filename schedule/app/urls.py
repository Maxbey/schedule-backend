from django.conf.urls import url, include
from django.contrib import admin
from rest_auth.views import LoginView, LogoutView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^api/', include('schedule.api.urls', namespace='api')),

    url(r'^api/v1/auth/login/$', LoginView.as_view(), name='rest_login'),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='rest_logout')
]

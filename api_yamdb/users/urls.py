from api.views import UserViewSet, send_confirmation_code, send_token
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path(
        'auth/token/',
        send_token,
        name='send_token'),
    path(
        'auth/signup/',
        send_confirmation_code,
        name='send_confirmation_code')
]

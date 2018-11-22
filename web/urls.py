from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'userLog', userLog, name="userlog"),
    ]
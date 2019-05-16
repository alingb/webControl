from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'userLog', userLog, name="userlog"),
    url(r'status', status, name="status"),
    url(r'data/$', dataSource, name="dataSource"),
    url(r'envi/$', envirmentData, name="envirmentData"),
    url(r'real/$', realTimeStatus, name="realTimeStatus"),
    url(r'data/request$', dataSourceRequest, name="dataSourceRequest"),
    url(r'envi/request$', envirmentDataRequest, name="envirmentDataRequest"),
    url(r'real/request$', realTimeStatusRequest, name="realTimeStatusRequest"),
    ]

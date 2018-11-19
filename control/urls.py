from django.conf.urls import url
from .views import *

urlpatterns = [
    # url(r'index', index, name='index'),
    url(r'detail/(?P<ID>.*)', controlDeatil, name='controldetail'),
    url(r'serverdetail', serverDetail, name='serverdetail'),
    url(r'bios', bios, name='bios'),
    url(r'execute', execute, name='execute'),
    url(r'serverinfo', serverInfo, name='serverinfo'),
    url(r'mkexec', control, name="control"),
    url(r'infopaser', infoPaser, name="infopaser"),
    url(r'msgParsePost', msgParsePost, name="msgParsePost"),
]

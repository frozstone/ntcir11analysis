from django.conf.urls import url
from compare import views

urlpatterns = [url(r'^$', views.index, name='index'), url(r'^index/$', views.index, name='index'), url(r'^ajax/$', views.ajax, name='ajax'), ]

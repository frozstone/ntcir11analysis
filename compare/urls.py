from django.conf.urls import url
from compare import views

urlpatterns = [url(r'^$', views.index, name='index'),]

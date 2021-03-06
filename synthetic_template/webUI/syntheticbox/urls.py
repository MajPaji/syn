from django.conf.urls import url

from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 

app_name = 'syntheticbox'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^proc_data_dash/$', views.proc_data_dash, name='proc_data_dash'),
    url(r'^proc_json_processing/$', views.proc_json_processing, name='proc_json_processing'),
    url(r'^res_json_processing_plot/$', views.res_json_processing_plot, name='res_json_processing_plot'),
    url(r'^res_json_processing/$', views.res_json_processing, name='res_json_processing'),
    url(r'^res_json_processing_after/$', views.res_json_processing_after, name='res_json_processing_after'),
]

urlpatterns += staticfiles_urlpatterns()
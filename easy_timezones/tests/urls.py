from django.urls import path

from easy_timezones.tests import views

urlpatterns = [
    path('without_tz/', views.without_tz, name='without_tz'),
    path('with_tz/', views.with_tz, name='with_tz'),
]

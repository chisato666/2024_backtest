from django.urls import path, include
from . import views
from .views import graph_view



urlpatterns = [
     path('submit_backtest', views.submit_backtest),
     path('check_alert', views.check_alert),

     path('show_alert', views.show_alert),
     path('research', views.research),
     path('submit_research', views.submit_research),

     path('', views.say_hello),
     path('getProfiles',views.getProfiles, name='getProfiles'),
     path('get_btcusdt_price', views.get_btcusdt_price, name='get_btcusdt_price'),
     path('graph/', graph_view, name='graph'),
     path("backtest/", views.backtest_view, name='backtest'),

     path('ajax/',views.ajax)


]


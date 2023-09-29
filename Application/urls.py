from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import  views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('signup/', views.signup_view, name="signup"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name="logout"),
    path('transfer/', views.money_transfer, name='money_transfer'),
    path('list-charity/', views.list_charity, name='list_charity'),
    path('profile/', views.profile_settings, name="profile_settings"),
    path('trading/', views.trading, name="trading"),

    path('dashboard/', views.dashboard, name='dashboard'),
    # path('dashboard/transfer/', views.money_transfer, name='money_transfer'),
    # path('dashboard/list-charity/', views.list_charity, name='list_charity'),
    # path('dashboard/logout/', views.logout_view, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
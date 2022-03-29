"""simple_votings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
            extra_context={'menu': views.get_menu_context(), 'pagename': 'Авторизация'}
        ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registration/', views.registration_page, name='registration'),

    path('', views.index_page, name='index'),

    path('profile/', views.profile_page, name='profile'),

    path('voting/<int:id>/complaint/', views.complaint_page, name='complaint'),

    path('voting/list/', views.voting_list_page, name='voting_list'),
    path('voting/add/', views.voting_add_page, name='voting_add'),
    path('voting/<int:id>/public/', views.voting_public_page, name='voting_public'),
    path('voting/<int:id>/edit/', views.voting_edit_page, name='voting_edit'),
    path('voting/<int:voting_id>/variants/<int:variant_id>/edit/', views.variant_change, name='variant_change'),
    path('voting/<int:voting_id>/variants/<int:variant_id>/delete/', views.variant_delete, name='variant_delete'),
    path('voting/<int:id>/delete/', views.voting_delete, name='voting_delete'),
    path('profile/<int:id>/edit/', views.profile_edit_page, name='profile_edit'),
    path('voting/<int:id>/results/', views.voting_results_page, name="voting_results"),
    # На будущее:
    # 'voting/<int:id>/' - детали голосования (доступные только автору, такие как время публикации и т.д.)
    # 'voting/<int:id>/delete/' - удаление голосования
]

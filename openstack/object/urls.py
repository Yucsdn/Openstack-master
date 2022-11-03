from django.urls import path
from . import views

app_name = 'object'
urlpatterns = [
    path('login/', views.login),
    path('get_token/', views.get_token),
    path('home/', views.home),
    path('home/console/', views.console, name='console'),
    path('home/instance/', views.instance, name='instance'),
    path('home/image/', views.image, name='image'),
    path('home/notwork/', views.notwork, name='notwork'),
    path('home/projects/', views.projects, name='projects'),
    path('home/users/', views.users, name='users'),
    path('home/groups/', views.groups, name='groups'),
    path('home/roles/', views.roles, name='roles'),
    path('groups_revise_delete/', views.groups_revise_delete),
    path('users_revise_delete/', views.users_revise_delete),
    path('roles_revise_delete/', views.roles_revise_delete),
    path('projects_revise_delete/', views.projects_revise_delete),
    path('instance_revise_delete/', views.instance_revise_delete),
    path('images_revise_delete/', views.images_revise_delete),
    path('groups_add/', views.groups_add),
    path('users_add/', views.users_add),
    path('roles_add/', views.roles_add),
    path('projects_add/', views.projects_add),
    path('instance_add/', views.instance_add),
    path('images_add/', views.images_add),
]

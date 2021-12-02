from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('',views.home_view, name='home_view' ),
    path('list/', views.PostListView.as_view(), name='post_list'),
    path('map_list_view/', views.map_view_list, name='map_list_view'),
    path('owner/<int:ayi>/', views.PostListView.as_view(), name='post_list'),
    path('', views.post_list, name='post_list'),
    path('property/<int:pk>-<slug:slug>/', views.post_detail, name='post_detail'),
    path('new/', views.PostCreateView.as_view(), name='post'),
    path('update/<int:pk>-<slug:slug>/', views.PostUpdateView.as_view(), name='post_update'),
    path('delete/<int:pk>-<slug:slug>/', views.PostDeleteView.as_view(), name='post_delete'),
    path('filter/', views.filter_page, name='filter_page'),
    path('your_properties/', views.ProfileListView.as_view(), name='your_properties'),
    path('upload_pictures/<int:pk>-<slug:slug>/', views.property_picture_form, name='property_picture_form'),
    path('picture_delete/<int:pk>/', views.PictureDeleteView.as_view(), name='picture_delete'),
    path('upload_plan/<int:pk>-<slug:slug>/', views.property_plan_form, name='property_plan_form'),
    path('property_save/<int:pk>/', views.property_save),   
  
]

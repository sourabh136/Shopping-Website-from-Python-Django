from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='shophome'),
    path('about/', views.about, name='AboutUS'),
    path('contact/', views.contact, name='ContactUS'),
    path('tracker/', views.tracker, name='TrackingStatus'),
    path('search/', views.search, name='Search'),
    path('products/<int:myid>', views.productView, name='Productview'),
    path('checkout/', views.checkout, name='Checkout'),
    path('wishlist/', views.wishlist, name='Wishlist'),
    path('compare/', views.compare, name='Compare'),
    path('handlerequest/', views.handlerequest, name='handleRequest'),


]
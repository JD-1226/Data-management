from django.urls import path
from . import views


urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:book_id>/', views.return_book, name='return_book'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-book/', views.add_book, name='add_book'),
]
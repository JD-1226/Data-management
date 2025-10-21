from django.urls import path
from . import views

urlpatterns = [
    # Home → now acts as login (as per your last setup idea)
    path('', views.login_user, name='home'),

    # Auth routes
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),

    # User dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('books/return/<int:copy_id>/', views.return_book, name='return_book'),

    # Add book (staff only)
    path('add-book/', views.add_book, name='add_book'),
]

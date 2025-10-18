from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, date
from .models import Book
from .forms import BookForm
from django.contrib.auth.models import User


# Create your views here.
def book_list(request):
    books = Book.objects.all()
    return render(request, 'library_app/book_list.html', {'books': books})


@login_required(login_url='/login/')
def user_dashboard(request):
    borrowed_books = Book.objects.filter(borrower=request.user)
    today = date.today()
    return render(request, 'library_app/dashboard.html', {
        'borrowed_books': borrowed_books,
        'today': today
    })


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.available:
        book.available = False
        book.borrower = request.user
        book.borrowed_date = timezone.now().date()
        book.due_date = timezone.now().date() + timedelta(days=7)
        book.save()
    return redirect('user_dashboard')


@login_required
def return_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, borrower=request.user)
    book.available = True
    book.borrower = None
    book.borrowed_date = None
    book.due_date = None
    book.save()
    return redirect('user_dashboard')


@staff_member_required
def admin_dashboard(request):
    total_books = Book.objects.count()
    borrowed_books = Book.objects.filter(available=False).count()
    available_books = total_books - borrowed_books
    total_users = User.objects.count()
    users_with_books = Book.objects.filter(borrower__isnull=False).values('borrower').distinct().count()

    return render(request, 'library_app/admin_dashboard.html', {
        'total_books': total_books,
        'borrowed_books': borrowed_books,
        'available_books': available_books,
        'total_users': total_users,
        'users_with_books': users_with_books,
    })


def add_book(request):
    if not request.user.is_staff:  # only staff can add books
        messages.error(request, "You don't have permission to add books.")
        return redirect('home')  # redirect to home or dashboard

    form = BookForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
            return redirect('book_list')  # go back to books list

    return render(request, 'library_app/add_book.html', {'form': form})
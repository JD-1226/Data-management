from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, date
from .models import Book, BookCopy
from .forms import BookForm
from django.contrib.auth.models import User


# Create your views here.
@login_required
def book_list(request):
    q = request.GET.get('q', '').strip()
    books_qs = Book.objects.all().prefetch_related('copies')

    if q:
        books_qs = books_qs.filter(title__icontains=q) | books_qs.filter(author__icontains=q)

    # Compute availability and whether the current user has a copy
    books = []
    for b in books_qs:
        # use the model property (this still hits DB but prefetch_related reduces queries for copies)
        b.available_copies = b.available_copies_count

        # See if current user already borrowed a copy of this book
        borrowed_copy = b.user_borrowed_copy(request.user)
        b.user_has_copy = bool(borrowed_copy)
        b.user_borrowed_copy_id = borrowed_copy.id if borrowed_copy else None

        books.append(b)

    return render(request, 'library_app/book_list.html', {
        'books': books,
        'query': q
    })

@login_required(login_url='/login/')
def user_dashboard(request):
    borrowed_books = BookCopy.objects.filter(borrower=request.user)
    today = date.today()
    return render(request, 'library_app/dashboard.html', {
        'borrowed_books': borrowed_books,
        'today': today
    })


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    copy = book.copies.filter(available=True).first()
    if not copy:
        messages.error(request, "All copies are currently borrowed.")
        return redirect('book_list')

    # prevent user from borrowing a second copy of same title (optional)
    if book.copies.filter(borrower=request.user, available=False).exists():
        messages.info(request, "You already borrowed a copy of this book.")
        return redirect('book_list')

    copy.available = False
    copy.borrower = request.user
    copy.borrowed_date = date.today()
    # optionally set due_date here
    copy.save()

    messages.success(request, f"You successfully borrowed '{book.title}'.")
    return redirect('book_list')


@login_required
def return_book(request, copy_id):
    copy = get_object_or_404(BookCopy, id=copy_id, borrower=request.user, available=False)
    copy.available = True
    copy.borrower = None
    copy.borrowed_date = None
    copy.due_date = None
    copy.save()
    messages.success(request, f"You returned '{copy.book.title}'.")
    return redirect('user_dashboard')


@staff_member_required
def admin_dashboard(request):
    total_books = Book.objects.count()
    total_copies = BookCopy.objects.count()
    borrowed_books = BookCopy.objects.filter(available=False).count()
    available_books = total_books - borrowed_books
    total_users = User.objects.count()
    users_with_books = (
        BookCopy.objects.filter(borrower__isnull=False)
        .values('borrower')
        .distinct()
        .count()
    )

    return render(request, 'library_app/admin_dashboard.html', {
        'total_books': total_books,
        'total_copies': total_copies,
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


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')
    return render(request, 'register.html')



def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {username}!")
            return redirect('book_list')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You’ve been logged out.")
    return redirect('login')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import date
from .models import Book, BookCopy
from .forms import BookForm


# -------------------------
# HOME (Login page)
# -------------------------
def home(request):
    """
    If user is authenticated, redirect based on role.
    Otherwise, show the login page.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('user_dashboard')
    return render(request, 'library_app/login.html')


# -------------------------
# USER AUTHENTICATION
# -------------------------
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")

            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('home')

    # GET request
    return render(request, 'library_app/login.html')


def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')

        if not all([username, email, password, confirm]):
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('home')

    return render(request, 'library_app/register.html')


# -------------------------
# USER DASHBOARD
# -------------------------
@login_required(login_url='/')
def user_dashboard(request):
    borrowed_books = BookCopy.objects.filter(borrower=request.user)
    today = date.today()
    return render(request, 'library_app/dashboard.html', {
        'borrowed_books': borrowed_books,
        'today': today,
    })


# -------------------------
# ADMIN DASHBOARD
# -------------------------
@staff_member_required
def admin_dashboard(request):
    total_books = Book.objects.count()
    total_copies = BookCopy.objects.count()
    borrowed_books = BookCopy.objects.filter(available=False).count()
    available_books = total_copies - borrowed_books
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


# -------------------------
# BOOK MANAGEMENT
# -------------------------
@login_required(login_url='/')
def book_list(request):
    q = request.GET.get('q', '').strip()
    books_qs = Book.objects.all().prefetch_related('copies')

    if q:
        books_qs = books_qs.filter(title__icontains=q) | books_qs.filter(author__icontains=q)

    books = []
    for book in books_qs:
        book.available_copies = book.available_copies_count
        borrowed_copy = book.user_borrowed_copy(request.user)
        book.user_has_copy = bool(borrowed_copy)
        book.user_borrowed_copy_id = borrowed_copy.id if borrowed_copy else None
        books.append(book)

    return render(request, 'library_app/book_list.html', {
        'books': books,
        'query': q,
    })


@login_required(login_url='/')
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    copy = book.copies.filter(available=True).first()

    if not copy:
        messages.error(request, "All copies are currently borrowed.")
        return redirect('book_list')

    if book.copies.filter(borrower=request.user, available=False).exists():
        messages.warning(request, "You already borrowed a copy of this book.")
        return redirect('book_list')

    copy.available = False
    copy.borrower = request.user
    copy.borrowed_date = date.today()
    copy.save()

    messages.success(request, f"You successfully borrowed '{book.title}'.")
    return redirect('book_list')


@login_required(login_url='/')
def return_book(request, copy_id):
    copy = get_object_or_404(BookCopy, id=copy_id, borrower=request.user, available=False)
    copy.available = True
    copy.borrower = None
    copy.borrowed_date = None
    copy.due_date = None
    copy.save()
    messages.success(request, f"You returned '{copy.book.title}'.")
    return redirect('user_dashboard')


# -------------------------
# ADMIN: ADD BOOK
# -------------------------
@staff_member_required
def add_book(request):
    form = BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Book added successfully!")
        return redirect('book_list')

    return render(request, 'library_app/add_book.html', {'form': form})

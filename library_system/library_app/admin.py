from django.contrib import admin
from .models import Book

# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available', 'borrower', 'due_date')
    list_filter = ('available', 'author')
    search_fields = ('title', 'isbn', 'borrower__username')
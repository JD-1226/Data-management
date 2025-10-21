from django.contrib import admin
from .models import Book, BookCopy

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'total_copies', 'available_copies')

    def total_copies(self, obj):
        return obj.copies.count()
    total_copies.short_description = 'Total Copies'

    def available_copies(self, obj):
        return obj.copies.filter(available=True).count()
    available_copies.short_description = 'Available Copies'


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book', 'available', 'borrower', 'due_date')
    list_filter = ('available', 'due_date')

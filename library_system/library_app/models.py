from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title 
    

    @property
    def available_copies_count(self):
        # This runs a simple count on related BookCopy objects.
        # Prefer calling this from the view or using it in templates (it will do one query per book unless prefetching).
        return self.copies.filter(available=True).count()

    def user_borrowed_copy(self, user):
        """Return BookCopy instance borrowed by user if any, else None."""
        if not user.is_authenticated:
            return None
        return self.copies.filter(borrower=user, available=False).first()


class BookCopy(models.Model):
    book = models.ForeignKey(Book, related_name='copies', on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    borrowed_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book.title} - {'Available' if self.available else 'Borrowed'}"
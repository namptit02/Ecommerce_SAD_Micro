from django.urls import path
from model import views

urlpatterns = [
    path('books', view = views.books, name = 'books'),
]

import re
from bson import ObjectId
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from book.decorators import verify_token, check_permission
from category.models import Category
from constants import PER_PAGE
from helpers import response_success, handle_query, response_error
from model.models import Book, BOOK_STATUS
from model.requests import create_and_update_schema
from model.serializers import BookSerializer
from model.validator import BookValidator
from rest_framework import status as http_status
from ast import literal_eval


# Create your views here.

# @verify_token
@api_view(['GET'])
def books(request):
    queries = handle_query(request)

    if queries['category_id'] is not None:
        if not ObjectId.is_valid(queries['category_id']):
            return response_error('Category ID must be an ObjectId.')

        exist_category = Category.objects.filter(_id = ObjectId(queries['category_id']), deleted = 0)
        if not exist_category:
            return response_error('Category does not exist.')

    book_list = (Book.objects
                 .filter(deleted = 0, status = BOOK_STATUS['AVAILABLE'])
                 .order_by(queries['field']))

    if queries['q'] is not None:
        book_list = book_list.filter(
            Q(title__icontains = queries['q'].strip()) |
            Q(code__icontains = queries['q'].strip())
        )

    if queries['category_id'] is not None:
        book_list = book_list.filter(categories___id = ObjectId(queries['category_id']))

    book_list = book_list[queries['from_page']:queries['to_page']]

    response_data = {
        'page': queries['page'],
        'per_page': PER_PAGE,
        'total': len(book_list),
        'books': BookSerializer(book_list, many = True).data
    }
    print(response_data)
    return response_success('Success', response_data)


@verify_token
@check_permission
@api_view(['GET'])
def admin_get_books(request):
    queries = handle_query(request)
    book_list = Book.objects.filter(deleted = 0).order_by(queries['field'])

    if queries['q'] is not None:
        q = queries['q'].strip()
        book_list = book_list.filter(Q(title__icontains = q) | Q(code__icontains = q))

    book_list = book_list[queries['from_page']:queries['to_page']]

    response_data = {
        'page': queries['page'],
        'per_page': PER_PAGE,
        'total': len(book_list),
        'books': BookSerializer(book_list, many = True).data
    }

    return response_success('Success', response_data)


@verify_token
@check_permission
@api_view(['POST'])
def create(request):
    (title, description, author, price,
     old_price, status, quantity, category_ids, image) = prepare_request(request)

    book = {
        'code': create_new_code(),
        'title': title,
        'description': description,
        'author': author,
        'price': int(price),
        'old_price': int(old_price) if old_price is not None else None,
        'status': int(status),
        'quantity': int(quantity),
        'image': image,
    }

    validator = BookValidator(create_and_update_schema)
    if validator.validate(book):
        try:
            new_book = Book.objects.create(**book)
            category_ids = [ObjectId(category_id) for category_id in literal_eval(category_ids)]
            categories = Category.objects.filter(_id__in = category_ids, deleted = 0)
            new_book.categories.set(categories)

            return response_success('Created successfully')
        except Exception as e:
            return response_error('Error', http_status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response_error('Error', http_status.HTTP_400_BAD_REQUEST, validator.errors)


@verify_token
@check_permission
@api_view(['PUT'])
def update(request, id):
    # validate
    if not ObjectId.is_valid(id):
        return response_error('Book ID must be an ObjectId.', http_status.HTTP_400_BAD_REQUEST)

    book = Book.objects.filter(_id = ObjectId(id), deleted = 0)
    if not book:
        return response_error('Book does not exist.', http_status.HTTP_400_BAD_REQUEST)

    book = book[0]
    (title, description, author, price,
     old_price, status, quantity, category_ids, image) = prepare_request(request)

    update_book = {
        'code': book.code,
        'title': title,
        'description': description,
        'author': author,
        'price': int(price),
        'old_price': int(old_price) if old_price is not None else None,
        'status': int(status),
        'quantity': int(quantity),
        'image': image,
    }

    validator = BookValidator(create_and_update_schema)
    if validator.validate(update_book):
        try:
            book.title = title
            book.description = description
            book.author = author
            book.price = price
            book.old_price = old_price
            book.status = status
            book.quantity = quantity
            book.category_ids = category_ids
            book.image = image
            book.save()

            category_ids = [ObjectId(category_id) for category_id in literal_eval(category_ids)]
            categories = Category.objects.filter(_id__in = category_ids, deleted = 0)
            book.categories.set(categories)

            return response_success('Updated successfully')
        except Exception as e:
            return response_error('Error', http_status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response_error('Error', http_status.HTTP_400_BAD_REQUEST, validator.errors)


@verify_token
@check_permission
@api_view(['DELETE'])
def delete(request, id):
    # validate
    if not ObjectId.is_valid(id):
        return response_error('Book ID must be an ObjectId.', http_status.HTTP_400_BAD_REQUEST)

    book = Book.objects.filter(_id = ObjectId(id), deleted = 0)
    if not book:
        return response_error('Book does not exist.', http_status.HTTP_404_NOT_FOUND)

    book = book[0]
    book.deleted = 1
    book.save()
    book.categories.clear()

    return response_success('Deleted Successfully')


def create_new_code():
    latest_book = Book.objects.all().order_by('-created_at').first()
    latest_code_number = int(re.findall(r'\d+', latest_book.code)[0]) if latest_book is not None else -1
    return 'B' + str(latest_code_number + 1)


def prepare_request(request):
    req = request.POST

    return [
        req.get("title"),
        req.get("description"),
        req.get("author"),
        req.get("price"),
        req.get("old_price"),
        req.get("status"),
        req.get("quantity"),
        req.get("category_ids"),
        request.FILES.get("image")
    ]

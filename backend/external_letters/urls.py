from django.urls import path
from .views import ExternalLetterViewSet, ExternalLettersCategoryViewSet

app_name = 'external_letters'

# category
category_list = ExternalLettersCategoryViewSet.as_view({'get': 'list'})
category_detail = ExternalLettersCategoryViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
category_create = ExternalLettersCategoryViewSet.as_view({'post': 'create'})
# letter
letter_list = ExternalLetterViewSet.as_view({'get': 'list'})
letter_detail = ExternalLetterViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
letter_create = ExternalLetterViewSet.as_view({'post': 'create'})

urlpatterns = [
    # categories
    path('categories/list/', category_list, name='category-list'),
    path('categories/create/', category_create, name='category-create'),
    path('categories/<slug:slug>/', category_detail, name='category-detail'),
    # letters
    path('letters/list/', letter_list, name='letter-list'),
    path('letters/create/', letter_create, name='letter-create'),
    path('letters/<slug:slug>/', letter_detail, name='letter-detail'),
]

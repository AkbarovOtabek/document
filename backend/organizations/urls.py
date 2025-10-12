from django.urls import path
from .views import CategoryViewSet, OrganizationViewSet

app_name = 'organizations'

# Category
category_list = CategoryViewSet.as_view({'get': 'list'})
category_detail = CategoryViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
category_create = CategoryViewSet.as_view({'post': 'create'})

# Organization
organization_list = OrganizationViewSet.as_view({'get': 'list'})
organization_detail = OrganizationViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
organization_create = OrganizationViewSet.as_view({'post': 'create'})

urlpatterns = [
    # Categories
    path('categories/list/', category_list, name='category-list'),
    path('categories/create/', category_create, name='category-create'),
    path('categories/<slug:slug>/', category_detail, name='category-detail'),

    # Organizations
    path('organizations/list/', organization_list, name='organization-list'),
    path('organizations/create/', organization_create, name='organization-create'),
    path('organizations/<slug:slug>/',
         organization_detail, name='organization-detail'),
]

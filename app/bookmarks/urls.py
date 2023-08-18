from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from .views import *

schema_view = get_schema_view(
    openapi.Info(
        title="API for Bookmarks",
        default_version='v.0.1',
        description="API for Bookmarks for test Fruktorum",
        terms_of_service="https://t.me/mikholand",
        contact=openapi.Contact(email="mikholand@gmail.com"),
        license=openapi.License(name="Oleg Mikhno"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', BookmarkHome.as_view(), name='home'),

    path('bookmarks/add/', BookmarkCreateView.as_view(), name='add_bookmark'),
    path('bookmarks/<int:pk>/update/', BookmarkUpdateView.as_view(), name='update_bookmark'),
    path('bookmarks/<int:pk>/delete/', BookmarkDeleteView.as_view(), name='delete_bookmark'),

    path('api/bookmarks/', BookmarkHomeAPI.as_view(), name='api_bookmark'),
    path('api/bookmarks/add/', BookmarkCreateAPIView.as_view(), name='api_add_bookmark'),
    path('api/bookmarks/<int:pk>/update/', BookmarkUpdateAPIView.as_view(), name='api_update_bookmark'),
    path('api/bookmarks/<int:pk>/delete/', BookmarkDeleteAPIView.as_view(), name='api_delete_bookmark'),

    path('collections/', CollectionListView.as_view(), name='collections'),
    path('collections/<int:collection_id>/', CollectionBookmarksView.as_view(), name='collection_bookmarks'),
    path('collections/add/', CollectionCreateView.as_view(), name='add_collection'),
    path('collections/<int:pk>/update/', CollectionUpdateView.as_view(), name='update_collection'),
    path('collections/<int:pk>/delete/', CollectionDeleteView.as_view(), name='delete_collection'),

    path('api/collections/', CollectionListAPIView.as_view(), name='api_collections'),
    path('api/collections/<int:collection_id>/', CollectionBookmarksAPIView.as_view(), name='api_collection_bookmarks'),
    path('api/collections/add/', CollectionCreateAPIView.as_view(), name='api_add_collection'),
    path('api/collections/<int:pk>/update/', CollectionUpdateAPIView.as_view(), name='api_update_collection'),
    path('api/collections/<int:pk>/delete/', CollectionDeleteAPIView.as_view(), name='api_delete_collection'),

    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, cbv_views, api_views
from .viewsets import CategoryViewSet, TagViewSet, EventViewSet

app_name = 'events'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', views.event_list, name='event-list'),
    path('event/<slug:slug>/', views.event_detail, name='event-detail'),
    path('category/<slug:category_slug>/', views.events_by_category, name='events-by-category'),
    path('api/cbv/events/', cbv_views.EventListCreateGenericView.as_view(), name='generic-event-list'),
    path('api/cbv/events/<int:pk>/', cbv_views.EventRetrieveUpdateDestroyGenericView.as_view(), name='generic-event-detail'),
    path('api/v1/summary/', cbv_views.PlatformSummaryAPIView.as_view(), name='platform-summary'),
    path('api/v1/', include(router.urls)),
    path('api/categories/', api_views.category_list_api, name='api-category-list'),
    path('api/categories/<int:pk>/', api_views.category_detail_api, name='api-category-detail'),
    path('api/tags/', api_views.tag_list_create_api, name='api-tag-list'),
]
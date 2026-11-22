from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Tag, Event
from .serializers import (
    CategorySerializer,
    TagSerializer,
    EventModelSerializer,
    EventListSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.events.exists():
            return Response(
                {"error": "Nie można usunąć kategorii, do której są przypisane wydarzenia."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        category = self.get_object()
        events = category.events.filter(is_published=True).select_related('category', 'organizer').prefetch_related('tags')
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        tag = self.get_object()
        events = tag.events.filter(is_published=True).select_related('category', 'organizer').prefetch_related('tags')
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('category', 'organizer').prefetch_related('tags').all()

    def get_serializer_class(self):
        if self.action in ['list', 'upcoming', 'free_events']:
            return EventListSerializer
        return EventModelSerializer

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        upcoming_events = self.get_queryset().filter(
            is_published=True,
            date__gte=timezone.now()
        ).order_by('date')
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def free_events(self, request):
        free = self.get_queryset().filter(is_published=True, price=0)
        serializer = self.get_serializer(free, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def publish_toggle(self, request, pk=None):
        event = self.get_object()
        event.is_published = not event.is_published
        event.save(update_fields=['is_published', 'updated_at'])
        status_text = "opublikowane" if event.is_published else "ukryte"
        return Response({
            "message": f"Wydarzenie '{event.title}' zostało {status_text}.",
            "is_published": event.is_published
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], url_path='manage-tags')
    def manage_tags(self, request, pk=None):
        event = self.get_object()
        tag_id = request.data.get('tag_id')

        if tag_id is None or tag_id == '':
            return Response(
                {"error": "Pole 'tag_id' jest wymagane."},
                status=status.HTTP_400_BAD_REQUEST
            )

        tag = get_object_or_404(Tag, pk=tag_id)

        if request.method == 'POST':
            event.tags.add(tag)
        elif request.method == 'DELETE':
            event.tags.remove(tag)

        serializer = TagSerializer(event.tags.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        original = self.get_object()
        new_event = Event.objects.create(
            title=f"{original.title} (Kopia)",
            slug=f"{original.slug}-kopia-{int(timezone.now().timestamp())}",
            category=original.category,
            organizer=original.organizer,
            description=original.description,
            location=original.location,
            date=original.date + timedelta(days=7),
            capacity=original.capacity,
            price=original.price,
            is_published=False,
        )
        new_event.tags.set(original.tags.all())
        serializer = EventModelSerializer(new_event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
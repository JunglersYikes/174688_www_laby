from django.db.models import Count, Avg, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Event, Category, Tag
from .serializers import EventModelSerializer, EventListSerializer


class EventListAPIView(APIView):
    def get(self, request):
        events = Event.objects.filter(is_published=True).select_related('category', 'organizer').prefetch_related('tags')
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EventModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlatformSummaryAPIView(APIView):
    def get(self, request):
        now = timezone.now()
        stats = Event.objects.filter(is_published=True).aggregate(
            total_published_events=Count('id'),
            upcoming_events_count=Count('id', filter=Q(date__gte=now)),
            free_events_count=Count('id', filter=Q(price=0)),
            average_ticket_price=Avg('price'),
        )
        avg_price = stats['average_ticket_price']

        data = {
            "total_published_events": stats['total_published_events'],
            "upcoming_events_count": stats['upcoming_events_count'],
            "free_events_count": stats['free_events_count'],
            "categories_count": Category.objects.count(),
            "tags_count": Tag.objects.count(),
            "average_ticket_price": round(float(avg_price), 2) if avg_price is not None else 0.00,
        }
        return Response(data, status=status.HTTP_200_OK)


class EventListCreateGenericView(generics.ListCreateAPIView):
    queryset = Event.objects.select_related('category', 'organizer').prefetch_related('tags').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventListSerializer
        return EventModelSerializer


class EventRetrieveUpdateDestroyGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.select_related('category', 'organizer').prefetch_related('tags').all()
    serializer_class = EventModelSerializer
from django.contrib.auth.models import User
from events.models import Category, Event
from decimal import Decimal

eventspublished = Event.objects.filter(is_published = True).order_by("created_at")
for event in eventspublished:
    print(f"{event.title} - {event.is_published} - {event.created_at}")

limit50 = Event.objects.filter(capacity__gte=Decimal('50'))
for event in limit50:
    print(f"{event.title} - {event.capacity}")

free = Event.objects.filter(price=Decimal('0.00'))
freeEvents = 0
for event in free:
    freeEvents += 1
print(f'Łączna liczba darmowych wydarzeń: {freeEvents}')

eventPublished = Event.objects.get(id=1)
eventPublished.is_published = False
eventPublished.save()
print(f"{eventPublished.title} - {eventPublished.is_published}")
import io
from events.models import Event
from events.serializers import EventSerializer
from rest_framework.renderers import JSONRenderer
event = Event.objects.first()
serializer = EventSerializer(event)
json_bytes = JSONRenderer().render(serializer.data)
print(json_bytes)
b'{"id":1,"title":"Research","slug":"research","category_id":1,"organizer_id":1,"description":".","location":"UWM","date":"2026-10-12T14:59:56Z","capacity":1,"price":"0.00","is_published":false,"created_at":"2026-10-12T14:59:59.685166Z"}'


from rest_framework.parsers import JSONParser
stream = io.BytesIO(json_bytes)
data = JSONParser().parse(stream)
data['title'] = "Wydarzenie z deserializacji"
data['slug'] = "wydarzenie-z-deserializacji"
deserializer = EventSerializer(data=data)
print("Czy dane są poprawne?", deserializer.is_valid())
Czy dane są poprawne? True
new_event = deserializer.save()
print(f"Utworzono nowe wydarzenie o ID: {new_event.id}")
Utworzono nowe wydarzenie o ID: 5


invalid_data = {
    'title': '',
    'capacity': -10,
    'date': 'fgdsfgds'
}
bad_serializer = EventSerializer(data=invalid_data)
print("Czy dane są poprawne?", bad_serializer.is_valid())
Czy dane są poprawne? False
print(bad_serializer.errors)
{'title': [ErrorDetail(string='To pole nie może być puste.', code='blank')], 'slug': [ErrorDetail(string='To pole jest wymagane.', code='required')], 'category_id': [ErrorDetail(string='To pole jest wymagane.', code='required')], 'organizer_id': [ErrorDetail(string='To pole jest wymagane.', code='required')], 'description': [ErrorDetail(string='To pole jest wymagane.', code='required')], 'location': [ErrorDetail(string='To pole jest wymagane.', code='required')], 'date': [ErrorDetail(string='Wartość daty z czasem ma zły format. Użyj jednego z dostępnych formatów: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].', code='invalid')], 'capacity': [ErrorDetail(string='Upewnij się, że ta wartość jest większa lub równa 1.', code='min_value')]}


web: daphne codezone.asgi:application --port $PORT --bind 0.0.0.0
worker: python manage.py runworker channels --settings=codezone.settings -v2
release: python manage.py migrate

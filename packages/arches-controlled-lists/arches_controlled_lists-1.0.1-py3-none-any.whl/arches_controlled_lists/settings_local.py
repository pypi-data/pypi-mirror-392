
# ES setting to connect to arches dev dependencies
ELASTICSEARCH_HTTP_PORT = 9202  # this should be in increments of 200, eg: 9400, 9600, 9800
ELASTICSEARCH_HOSTS = [{"scheme": "http", "host": "localhost", "port": ELASTICSEARCH_HTTP_PORT}]

ALLOWED_HOSTS = ["*"]

PUBLIC_SERVER_ADDRESS = "http://127.0.0.1:8000/"

DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": 0,
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": "localhost",
        "NAME": "arches_controlled_lists",
        "OPTIONS": {},
        "PASSWORD": "postgis",
        "PORT": "5432",
        "POSTGIS_TEMPLATE": "template_postgis",
        "TEST": {
            "CHARSET": None,
            "COLLATION": None,
            "MIRROR": None,
            "NAME": None
        },
        "TIME_ZONE": None,
        "USER": "postgres"
    }
}

CELERY_BROKER_URL = "amqp://localhost:5674/"
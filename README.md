# choose_one

## Environment

### Example

```
APP_SECRET=
DEBUG_MODE=True

POSTGRES_USER=user
POSTGRES_PASSWORD=
POSTGRES_DB=db
DB_HOST=localhost
DB_PORT=5433

ACCESS_TOKEN_LIFETIME_HOURS=40
ACCESS_TOKEN_LIFETIME_MINUTES=0
REFRESH_TOKEN_LIFETIME_DAYS=7

API_VERSION=v0.1.0

EMAIL_USER=
EMAIL_PASSWORD=

BROKER_URL=

DJANGO_LOG_PATH=
CELERY_LOG_PATH=

HOST=

CORS_ORIGINS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOW_ALL=False
```

### Description

* `APP_SECRET` - random long secret key
* `DEBUG_MODE` - run upp in debug or prod mode. Set `True` to run in debug mode.

* `POSTGRES_USER` - the name of Postgres user.
* `POSTGRES_PASSWORD` - the password of Postgres user.
* `POSTGRES_DB` - the name of Postgres database.
* `DB_HOST` - database's host.
* `DB_PORT` - database's port.

* `ACCESS_TOKEN_LIFETIME_HOURS` - specifies how many hours access tokens are valid.
* `ACCESS_TOKEN_LIFETIME_MINUTES` - specifies how many minutes access tokens are valid.
* `REFRESH_TOKEN_LIFETIME_DAYS` - specifies how many days refresh tokens are valid.

* `API_VERSION` - API version.

* `EMAIL_USER` - Username to use for the SMTP server defined in `EMAIL_HOST`. If empty, Django won’t attempt authentication.
* `EMAIL_PASSWORD` - Password to use for the SMTP server defined in `EMAIL_HOST`. This setting is used in conjunction with `EMAIL_HOST_USER` when authenticating to the SMTP server. If either of these settings is empty, Django won’t attempt authentication.
* `BROKER_URL` - broker url for celery
* `DJANGO_LOG_PATH` - path to save django's logs
* `CELERY_LOG_PATH` - path to save celery's logs
* `HOST` - host of the site to include in `ALLOWED_HOSTS` constant
* `CORS_ORIGINS` - comma separated list of cors-allowed origins
* `CORS_ALLOW_ALL` - allow all origins. **NOTE** Use only for debug
purposes! Don't set it in `True` in production

## Test environment

For testing purposes we need all variables defined above and ones
from the list below
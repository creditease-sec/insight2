DEBUG = True

PORT = 8000

DB_HOST = 'web_mysql'
DB_PORT = 3306
DB_NAME = 'insight2'
DB_USER = 'root'
DB_PASS = 'crediteaseitsec'

REDIS_HOST = 'web_redis'
REDIS_PORT = 6379
REDIS_PASS = 'crediteaseitsec'
REDIS_DB = 0
REDIS_CHANNEL = "SERVICE_CHANNEL"


ACTION_DIR_NAME = ("action", )

STATIC_DIR_NAME = "static"

TEMPLATE_DIR_NAME = "template"

COOKIE_SECRET = "U2FsdGVkX1/u1YaeTuRdWM9adoqFpGm9seFRccbhRR/O2qyTwP78Cok="

API_VERSION = "/api"

FROM_DB = dict(
            host = 'web_mysql',
            port = 3306,
            user = "root",
            password = "crediteaseitsec",
            database = "insight"
        )


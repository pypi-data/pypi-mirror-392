SECRET_KEY = "test-secret-key"
DEBUG = True
USE_TZ = True
INSTALLED_APPS = [
    "rest_framework",
]
# DRF minimal default, no DB needed for these tests
REST_FRAMEWORK = {}

import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, os.path.dirname(PROJECT_ROOT))

DEBUG=True
TEMPLATE_DEBUG=True
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/flatblocks.db'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'modeltranslation',
    'flatblocks',
)
LANGUAGE_CODE="en"
USE_I18N = True
gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('es', gettext('Spanish')),
)
MODELTRANSLATION_TRANSLATION_REGISTRY = 'test_project.translation'
TRANSLATION_REGISTRY = MODELTRANSLATION_TRANSLATION_REGISTRY

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)
ROOT_URLCONF = 'test_project.urls'

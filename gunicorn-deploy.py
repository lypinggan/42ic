# Production WSGI configuration

import production_settings

from newsmeme import create_app

app = create_app(production_settings)


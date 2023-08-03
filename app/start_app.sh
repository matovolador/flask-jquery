#!/bin/bash
alembic upgrade head || exit 1
# python tests.py || exit 1
gunicorn --bind 0.0.0.0:5050 --certfile /etc/letsencrypt/live/<your_domain>/fullchain.pem --keyfile /etc/letsencrypt/live/<your_domain>/privkey.pem app:app 
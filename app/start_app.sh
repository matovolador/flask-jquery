#!/bin/bash
alembic upgrade head || exit 1
# python tests.py || exit 1
gunicorn --bind 0.0.0.0:5050 -w 3 app:app
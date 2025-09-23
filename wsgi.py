#!/usr/bin/env python3
"""
WSGI entry point para Gunicorn
"""

from app_aws import app

if __name__ == "__main__":
    app.run()

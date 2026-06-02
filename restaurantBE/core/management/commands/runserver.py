"""
Override Django's runserver to use uvicorn with ASGI.
Usage: python manage.py runserver
"""
import os
import sys
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run uvicorn ASGI server (replaces Django's built-in runserver)"

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport",
            nargs="?",
            default="0.0.0.0:8000",
            help="Optional address and port to bind to (default: 0.0.0.0:8000)",
        )
        parser.add_argument(
            "--noreload",
            action="store_true",
            help="Disable auto-reload on code changes",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=1,
            help="Number of worker processes (default: 1)",
        )

    def handle(self, *args, **options):
        import uvicorn

        addrport = options["addrport"]
        reload = not options["noreload"]
        workers = options["workers"]

        # Parse host:port
        if ":" in addrport:
            host, port = addrport.rsplit(":", 1)
            port = int(port)
        else:
            host = "0.0.0.0"
            port = int(addrport)

        self.stdout.write(
            self.style.SUCCESS(f"Starting uvicorn on http://{host}:{port}")
        )

        uvicorn.run(
            "restaurantBE.asgi:application",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level="info",
        )

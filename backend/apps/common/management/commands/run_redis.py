import time
import sys
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Starts a lightweight Redis-compatible TCP server on localhost:6379 for local development."

    def add_arguments(self, parser):
        parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
        parser.add_argument("--port", type=int, default=6379, help="Port to bind (default: 6379)")

    def handle(self, *args, **options):
        host = options["host"]
        port = options["port"]

        try:
            import fakeredis
            self.stdout.write(self.style.SUCCESS(f"Starting FlowOps Redis service on {host}:{port}..."))
            server = fakeredis.TcpFakeServer((host, port))
            self.stdout.write(self.style.SUCCESS(f"Redis service running at redis://{host}:{port}/0"))
            self.stdout.write(self.style.NOTICE("Press Ctrl+C to terminate."))
            server.serve_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nRedis service stopped."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to start Redis service: {e}"))
            sys.exit(1)


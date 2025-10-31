from django.core.management.base import BaseCommand, CommandError
from django.core.cache import caches, DEFAULT_CACHE_ALIAS


class Command(BaseCommand):
    help = (
        "Clear Django cache. By default clears the default cache. "
        "Optionally provide one or more cache keys to delete instead of clearing all."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--cache",
            dest="cache_alias",
            default=DEFAULT_CACHE_ALIAS,
            help="Cache alias to operate on (default: default)",
        )
        parser.add_argument(
            "keys",
            nargs="*",
            help="Specific cache key(s) to delete. If omitted, the entire cache will be cleared.",
        )

    def handle(self, *args, **options):
        alias = options.get("cache_alias")
        keys = options.get("keys") or []

        try:
            cache = caches[alias]
        except Exception as e:
            raise CommandError(f"Cannot access cache alias '{alias}': {e}")

        if keys:
            deleted = 0
            for key in keys:
                try:
                    if cache.delete(key):
                        deleted += 1
                except Exception as e:
                    self.stderr.write(f"Error deleting key {key}: {e}")
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} of {len(keys)} keys from cache '{alias}'."))
        else:
            try:
                cache.clear()
                self.stdout.write(self.style.SUCCESS(f"Cleared cache '{alias}'."))
            except NotImplementedError:
                raise CommandError(
                    "The configured cache backend does not support clearing via cache.clear()."
                )
            except Exception as e:
                raise CommandError(f"Failed to clear cache '{alias}': {e}")

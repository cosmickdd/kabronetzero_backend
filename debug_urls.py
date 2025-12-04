#!/usr/bin/env python
"""
URL Route Debugger - Lists all registered Django URL patterns
Run: python manage.py shell < debug_urls.py
"""

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def show_urls(urlpatterns, prefix=''):
    """Recursively display URL patterns"""
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            # This is an include() - recurse into it
            new_prefix = prefix + str(pattern.pattern)
            show_urls(pattern.url_patterns, new_prefix)
        elif isinstance(pattern, URLPattern):
            # This is a path/re_path
            route = prefix + str(pattern.pattern)
            print(f"✓ {route}")

# Get the main URL configuration
resolver = get_resolver()
print("\n=== All Registered URL Routes ===\n")
show_urls(resolver.url_patterns)
print("\n=== End of Routes ===\n")

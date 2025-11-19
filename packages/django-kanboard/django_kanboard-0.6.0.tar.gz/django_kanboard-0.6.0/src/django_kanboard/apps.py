"""
Apps entry for the :mod:`django_kanboard` application.

:creationdate: 28/06/2021 16:59
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_kanboard.apps
"""

from django.apps import AppConfig


class DjangoKanboardConfig(AppConfig):
    """Main django base config."""

    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "django_kanboard"

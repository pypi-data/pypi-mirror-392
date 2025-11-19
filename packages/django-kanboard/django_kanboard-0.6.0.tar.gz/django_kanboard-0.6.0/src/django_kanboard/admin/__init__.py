"""
Admin for :mod:`django_kanboard` application.

:creationdate: 28/06/2021 12:11
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_kanboard.admin

"""

import logging

from django.contrib import admin
from django.utils.translation import gettext as _
from solo.admin import SingletonModelAdmin

from django_kanboard import models

logger = logging.getLogger(__name__)
__author__ = "fguerin"


@admin.register(models.KanboardConfig)
class KanboardConfigAdmin(SingletonModelAdmin):
    """Simple settings admin."""

    fieldsets = [  # type: ignore
        (
            None,
            {
                "fields": (
                    "base_url",
                    "username",
                    "token",
                    "template_prefix",
                )
            },
        ),
    ]


@admin.register(models.ProjectTemplate)
class ProjectTemplateAdmin(admin.ModelAdmin):
    """Settings for the :class:`django_kanboard.models.ProjectTemplate` instances."""

    fieldsets = [  # type: ignore
        (
            None,
            {"fields": ("name", "description")},
        ),
    ]


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for :class:`django_kanboard.models.Project` instances."""

    list_display = (  # type: ignore
        "content_object",
        "project_template",
        "board_url",
    )

    fieldsets = (  # type: ignore
        (
            None,
            {
                "fields": (
                    "content_object",
                    "project_template",
                )
            },
        ),
        (
            _("Kanboard references"),
            {
                "fields": (
                    "kanboard_project_id",
                    "board_url",
                    "calendar_url",
                    "list_url",
                )
            },
        ),
    )

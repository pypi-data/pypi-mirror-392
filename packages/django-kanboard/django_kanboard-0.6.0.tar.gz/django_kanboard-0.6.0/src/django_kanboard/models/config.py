"""
Config models for :mod:`django_kanboard` application.

:creationdate: 28/06/2021 12:11
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_kanboard.models.config

"""

import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from solo.models import SingletonModel

logger = logging.getLogger(__name__)
__author__ = "fguerin"


class KanboardConfig(SingletonModel):
    """Scheduler application configuration."""

    # region Scheduler params
    base_url = models.URLField(
        verbose_name=_("base server URL"),
        blank=True,
    )

    username = models.CharField(
        verbose_name=_("username"),
        max_length=255,
        blank=True,
    )

    token = models.CharField(
        max_length=255,
        verbose_name=_("token"),
        blank=True,
    )

    template_prefix = models.CharField(
        verbose_name=_("template prefix"),
        max_length=255,
        blank=True,
        help_text=_("Templates are selected on the kanboard application using a specified prefix."),
    )
    # endregion Scheduler params

    class Meta(SingletonModel.Meta):
        """Metaclass for :class:`django_kanboard.models.config.KanboardConfig`."""

        verbose_name = _("Kanboard config")
        verbose_name_plural = _("Kanboard configs")

    def __str__(self) -> str:
        """
        Get the string representation of :class:`scheduler.models.SchedulerConfig*` instance.

        :return: Fixed string
        """
        return _("Kanboard config")

    # region Model validation
    def clean_scheduler(self) -> None:
        """
        Check the scheduler parameters.

        .. note:: This method raises :class:`django:django.core.exceptions.ValidationError` on invalid parameters.

        :return: Nothing
        """
        if self.base_url and not (self.username and self.token):
            raise ValidationError(
                {
                    "username": _("You must provide a username for Kanboard."),
                    "token": _("You must provide a password for Kanboard."),
                }
            )

    def clean(self) -> None:
        """
        Check for values before saving data.

        .. note:: This method raises :class:`django:django.core.exceptions.ValidationError` on invalid parameters.

        :return: Nothing
        """
        super().clean()
        self.clean_scheduler()

    # endregion Model validation

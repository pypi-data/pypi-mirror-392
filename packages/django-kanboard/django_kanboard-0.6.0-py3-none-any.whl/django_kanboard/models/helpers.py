"""
helpers for :mod:`django_kanboard.models` application.

:creationdate: 28/06/2021 13:30
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_kanboard.models.helpers

"""

import logging

from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django_currentuser.middleware import get_current_authenticated_user

__author__ = "fguerin"
logger = logging.getLogger(__name__)


class Administrable(models.Model):
    """An administrable model takes cares of when and who created and updated it."""

    #: Creation date as a :class:`python:datetime.datetime`
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True, editable=False)

    #: Update date as a :class:`python:datetime.datetime`
    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True, editable=False)

    #: Creator as a :class:`django:django.contrib.auth.models.User`
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("created by"),
        related_name="%(app_label)s_%(class)s_owned",
        default=1,
        on_delete=models.SET_DEFAULT,
        editable=False,
    )

    #: Updater as a :class:`django:django.contrib.auth.models.User`
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("updated by"),
        related_name="%(app_label)s_%(class)s_updated",
        null=True,
        on_delete=models.SET_NULL,
        editable=False,
    )

    class Meta:
        """Meta for class."""

        abstract = True

    def set_administrative_data(self):
        """
        Update the administrative fields of the Administrable models.

        .. note:: Hook method.

        :return: Nothing
        """
        current_user = get_current_authenticated_user()
        default_user = apps.get_model(settings.AUTH_USER_MODEL).objects.order_by("pk").first()

        if current_user is None:
            current_user = default_user
            logger.warning(
                "%s::set_administrative_data() Unable to get the current user_dict from local thread: "
                'setting the default one: "%s"',
                self.__class__.__name__,
                current_user,
            )

        # Looks like a n instance creation
        if self.updated_by is None and self.created_by == default_user:
            self.created_by = self.updated_by = current_user or default_user  # type: ignore
            logging.info(
                "%s::set_administrative_data() Creates a new instance of %s: created_by = %s",
                self.__class__.__name__,
                self,
                self.created_by,
            )
        else:
            self.updated_by = current_user or default_user  # type: ignore
            logging.info(
                "%s::set_administrative_data() Updates an existing instance (%s): updated_by = %s",
                self.__class__.__name__,
                self,
                self.updated_by,
            )

    def save_base(
        self,
        raw=False,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ) -> None:
        """
        Save the connected user_dict into the right field, according to the object state.

        + If the object is a new one: :attr:`account.models.helpers.Administrable.created_by`
        + If the object is NOT a new one: :attr:`account.models.helpers.Administrable.updated_by`

        :param raw: Raw SQL query ?
        :param force_insert: Force insertion
        :param force_update: Force update
        :param using:  DB alias used
        :param update_fields: List fields to update
        :return: Nothing
        """
        self.set_administrative_data()

        super().save_base(
            raw=raw,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

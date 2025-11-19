"""
forms for :mod:`django_kanboard.admin` application.

:creationdate: 28/06/2021 14:58
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_kanboard.admin.forms

"""

import logging

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.db.models import Q, QuerySet
from django.utils.translation import gettext as _
from django_ckeditor_5.widgets import CKEditor5Widget

from django_kanboard import models

__author__ = "fguerin"
logger = logging.getLogger(__name__)


def _get_user_queryset() -> QuerySet[auth_models.User]:  # type: ignore
    return apps.get_model(settings.AUTH_USER_MODEL).objects.filter(Q(is_staff=True) | Q(is_superuser=True))  # type: ignore


class UserModelChoiceField(forms.ModelChoiceField):
    """Custom ModelChoiceField to display user_dict full name instead of username."""

    def label_from_instance(self, obj):
        """
        Get the full name as option label.

        :param obj: Object instance
        :return: Full name
        """
        return obj.get_full_name()  # type: ignore


class ProjectTemplateForm(forms.ModelForm):
    """Admin form for :class:`scheduler.models.ProjectTemplate` instances."""

    owner = UserModelChoiceField(
        queryset=_get_user_queryset(),
        label=_("owner"),
    )

    class Meta:
        """Metaclass for :class:`django_kanboard.admin.forms.ProjectTemplateForm`."""

        model = models.ProjectTemplate
        fields = [
            "name",
            "description",
        ]
        widgets = {
            "description": CKEditor5Widget(),
        }

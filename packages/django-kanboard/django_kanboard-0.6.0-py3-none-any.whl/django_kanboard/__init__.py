"""
Django-kanboard application provides some projects schemas and a way to create projects in the kanboard application.

:creationdate: 28/06/21 16:29
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_kanboard
"""

from django_kanboard.__about__ import __version__
from django_kanboard.kanboard_wrapper import KanboardSyncer, KanboardUpdater, KanboardWrapper

__author__ = "fguerin"
VERSION = __version__
__all__ = [
    "KanboardSyncer",
    "KanboardWrapper",
    "KanboardUpdater",
]

"""
sync_project_templates command.

:creationdate: 28/06/2021 15:37
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_kanboard.management.commands.sync_project_templates

"""

import logging

from django.core.management import BaseCommand

from django_kanboard import models
from django_kanboard.kanboard_wrapper import KanboardSyncer, WrapperError

__author__ = "$USER"
logger = logging.getLogger("${MODULE}.management.commands.${NAME}")


class Command(BaseCommand):
    """Command."""

    help = "Keep kanboard templates in sync with reqistered templates."
    verbosity = None
    dry_run = True

    def add_arguments(self, parser):
        """
        Ass arguments to the parser.

        :param parser: Args parser
        :return: Nothing
        """
        parser.add_argument(
            "-s",
            "--base-url",
            dest="base_url",
            action="store",
            help="Kanboard server API URL",
        )
        parser.add_argument(
            "-u",
            "--username",
            dest="username",
            action="store",
            help="Kanboard username",
        )
        parser.add_argument(
            "-t",
            "--token",
            dest="token",
            action="store",
            help="Kanboard user_dict token",
        )
        parser.add_argument(
            "-n",
            "--dry-run",
            dest="dry_run",
            action="store_true",
            default=False,
            help="If set, no actions are performed to database.",
        )

    def handle(self, *args, **options):  # type: ignore
        """
        Handle the command.

        :param args: Args
        :param options: Options, from the parser
        :return: 0 if success, something else otherwise.
        """
        self.verbosity = options.get("verbosity")
        dry_run = options.get("dry_run")

        base_url = options.get("base_url")
        username = options.get("username")
        token = options.get("token")

        # Get the params from command options or from config
        if base_url is None or username is None or token is None:
            _config: models.KanboardConfig = models.KanboardConfig.get_solo()
            base_url = base_url or _config.base_url
            username = username or _config.username
            token = token or _config.token

        # Synchronize stuff
        try:
            syncer = KanboardSyncer(base_url=base_url, username=username, token=token, dry_run=dry_run)  # type: ignore
            syncer.sync_templates()
            syncer.sync_users()
            syncer.sync_groups()
        except WrapperError as e:
            logger.fatal(str(e))
            return 1
        return 0

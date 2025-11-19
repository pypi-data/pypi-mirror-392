"""
templates_syncer for :mod:`django_kanboard` application.

:creationdate: 28/06/2021 15:54
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_kanboard.templates_syncer

"""

import logging
import pprint
from datetime import datetime
from typing import Any

import kanboard
from django.contrib.auth import models as auth_models
from django.utils.text import slugify

from django_kanboard import models

__author__ = "fguerin"
logger = logging.getLogger(__name__)


class WrapperError(Exception):
    """Generic exception for syncer."""

    pass


class KanboardWrapper:
    """Connect the application to the Kanboard application."""

    _client: kanboard.Client | None = None

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        token: str | None = None,
    ):
        """
        Initialize the :class:`django_kanboard.templates_syncer.KanboardWrapper` instance.

        :param base_url: Base kanboard URL (optional)
        :param username:  Kanboard username (optional)
        :param token:  Kanboard token (optional)
        """
        if base_url is None or username is None or token is None:
            _config: models.KanboardConfig = models.KanboardConfig.get_solo()
            base_url = base_url or _config.base_url  # type: ignore
            username = username or _config.username  # type: ignore
            token = token or _config.token  # type: ignore

        self._base_url = base_url
        self._username = username
        self._token = token

    @property
    def client(self):
        """
        Initialize the client connection to the Kanboard instance.

        :return: Initialized client instance
        """
        if self._client:
            return self._client
        self._client = kanboard.Client(
            url=self._base_url,  # type: ignore
            username=self._username,  # type: ignore
            password=self._token,  # type: ignore
        )
        return self._client


class KanboardUpdater(KanboardWrapper):
    """Kanboard project creation an copy management."""

    def get_kanboard_user_id(self, user: auth_models.User | int) -> int:
        """
        Get the kanboard user id.

        :param user: Django User or user id.
        :return:  Kanboard user id
        """
        _user = user if isinstance(user, auth_models.User) else auth_models.User.objects.get(id=user)
        if hasattr(_user, "kanboard_user"):
            return _user.kanboard_user.kanboard_user_id

        kb_user = self.client.get_user_by_name(username=_user.username)
        new_rel = models.KanboardUser.objects.create(user=_user, kanboard_user_id=int(kb_user["id"]))  # type: ignore
        return int(new_rel.kanboard_user_id)

    def _get_tasks(
        self,
        project_id: int,
    ) -> list[dict[str, Any]]:
        """
        Get the tasks for a given kanboard project.

        :param project_id: Project identifier
        :return: List of tasks.
        """
        project_tasks = self.client.get_all_tasks(
            project_id=project_id,
            status_id=1,
        )
        # Get subtasks
        for task in project_tasks:  # type: ignore
            subtasks = self.client.get_all_subtasks(task_id=task["id"])
            task["subtasks"] = subtasks
        return project_tasks  # type: ignore

    def get_project_dict(self, project_id: int, with_tasks: bool = True) -> dict[str, Any]:
        """
        Get a project template from the kanboard application.

        :param project_id: Project identifier
        :param with_tasks: If `True`, tasks will be also grabbed and added into a 'tasks' key.
        :return: Kanboard project, used as template
        """
        _project_dict = self.client.get_project_by_id(project_id=project_id)
        if _project_dict is None:
            raise WrapperError(f"Unable to get project from Kanboard server with ID = {project_id}")
        if with_tasks:
            _project_dict["tasks"] = self._get_tasks(project_id=project_id)  # type: ignore
        return _project_dict  # type: ignore

    def copy_project(self, from_project_id: int, **kwargs) -> dict[str, Any]:
        """
        Create a project from a copy of an existing template.

        :param from_project_id: Template project identifier
        :param kwargs: Extra kwargs
        :return: Created project
        """
        _config = models.KanboardConfig.get_solo()
        kb_project_template: dict[str, Any] = self.get_project_dict(project_id=from_project_id)  # type: ignore
        logger.debug(
            "%s::copy_project() kb_project_template = %s",
            self.__class__.__name__,
            pprint.pformat(kb_project_template),
        )

        name = kwargs.get("title") or kwargs.get("name")

        if not name:
            name = kb_project_template["name"][len(_config.template_prefix) :].strip()  # noqa
        user = kwargs.get("user")
        user_id = kwargs.get("user_id")
        owner_id = self.get_kanboard_user_id(user or user_id)
        description = kwargs.get("description") or kb_project_template["description"]
        start_date = kwargs.get("start_date") or kb_project_template.get("start_date")
        end_date = kwargs.get("end_date") or kb_project_template.get("end_date")
        project_id = self.create_project(
            name=name,
            owner_id=owner_id,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )
        if not project_id:
            raise WrapperError(f"Unable to copy project from {from_project_id}.")

        logger.info(
            "%s::copy_project() Project copied from %s  with id = %s",
            self.__class__.__name__,
            from_project_id,
            project_id,
        )
        tasks = kb_project_template.get("tasks")
        if tasks:
            new_tasks = self._add_tasks(project_id=project_id, tasks=tasks, owner_id=owner_id)
            logger.info(
                "%s::copy_project() Tasks %s copied from %s with id = %s",
                self.__class__.__name__,
                pprint.pformat(new_tasks),
                from_project_id,
                project_id,
            )

        return self.get_project_dict(project_id=project_id, with_tasks=False)

    def create_project(  # noqa: CFQ002
        self,
        name: str,
        owner_id: int,
        identifier: str | None = None,
        description: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """
        Create a project with the given informations.

        :param name: Project name
        :param owner_id: Project owner
        :param identifier: Project internal identifier
        :param description: Project description
        :param start_date: Start at
        :param end_date: End at
        :return: New project identifier
        """
        # Check for user
        if not self.client.get_user(user_id=owner_id):
            raise WrapperError(f"Unable to create a project: user {owner_id} does nor exists on kanboard application.")

        params = {
            "name": name,
            "owner_id": owner_id,
        }

        if identifier:
            params.update(
                {
                    "identifier": slugify(identifier).replace("-", "").upper(),  # type: ignore
                }
            )

        if description:
            params.update({"description": description})

        if start_date and isinstance(start_date, datetime):
            params.update({"start_date": start_date.strftime("%Y-%m-%d")})

        if end_date and isinstance(end_date, datetime):
            params.update({"end_date": end_date.strftime("%Y-%m-%d")})

        project_id = self.client.create_project(**params)
        if not project_id:
            raise WrapperError(f"Unable to create project for user {owner_id} with name {name}")

        logger.info(
            "%s::create_project() Project created with id = %s",
            self.__class__.__name__,
            project_id,
        )
        # Make the project public
        _project_id = int(project_id)  # type: ignore
        result = self.client.enable_project_public_access(project_id=_project_id)
        if not result:
            logger.warning(
                "%s::create_project() Unable to make project with id = %s public.",
                self.__class__.__name__,
                project_id,
            )
        return _project_id

    def remove_project(self, project_id: int) -> bool:
        """
        Delete a project on the kanboard application.

        :param project_id: Project identifier
        :return: `True` on success
        """
        deleted = self.client.remove_project(project_id=project_id)
        if deleted:
            logger.info(
                "%s::remove_project() Project with id %s REMOVED.",
                self.__class__.__name__,
                project_id,
            )
            return deleted  # type: ignore
        raise WrapperError(f"Unable to remove project with id = {project_id}")

    def _add_subtasks(self, task_id: int, subtasks: list[dict[str, Any]]) -> list[int]:
        """
        Add subtasks to a given task.

        :param task: Parent task
        :param subtasks: List on subtasks to add
        :return: Nothing
        """
        new_subtasks = []
        for subtask in subtasks:
            new_subtask = self.client.create_subtask(
                task_id=task_id,
                title=subtask["title"],
                user_id=subtask.get("user_id"),
            )
            if not new_subtask:
                raise WrapperError(f"Unable to create subtask with title {subtask['title']} to task {task_id}")
            new_subtasks.append(int(new_subtask))  # type: ignore
        return new_subtasks

    def _add_tasks(self, project_id: int, tasks: list[dict[str, Any]], owner_id: int) -> list[dict[str, Any]]:
        new_tasks = []
        for task in tasks:
            subtasks = task.pop("subtasks")
            task.pop("project_id")
            task.pop("id")
            task.pop("date_creation")
            task.pop("date_modification")
            task.pop("date_moved")
            params = {
                "title": task["title"],
                "color_id": task["color_id"],
                "column_id": 0,
                "creator_id": owner_id,
                "description": task["description"],
                "category_id": task["category_id"],
            }
            new_task = self.client.create_task(project_id=project_id, **params)
            if not new_task:
                raise WrapperError(f"Unable to add task {task['name']} to project {project_id}")

            logger.info(
                "%s::_add_tasks() Task %s added to project %s",
                self.__class__.__name__,
                new_task,
                project_id,
            )
            new_subtasks = self._add_subtasks(task_id=new_task, subtasks=subtasks)  # type: ignore
            logger.info(
                "%s::_add_tasks() subtasks %s added to project %s",
                self.__class__.__name__,
                pprint.pformat(new_subtasks),
                project_id,
            )
            new_tasks.append(new_task)  # type: ignore
        return new_tasks


class KanboardSyncer(KanboardWrapper):
    """Keep local database in sync with kanboard data."""

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        token: str | None = None,
        dry_run: bool = False,
    ):
        """
        Initialize the :class:`django_kanboard.templates_syncer.KanboardSyncer` instance.

        :param base_url: Base kanboard URL (optional)
        :param username:  Kanboard username (optional)
        :param token:  Kanboard token (optional)
        :param dry_run: If `True`, no operations will be performed on the local database
        """
        super().__init__(base_url=base_url, username=username, token=token)
        self._dry_run = dry_run

    def sync_templates(self, template_prefix: str | None = None) -> None:
        """
        Get the template from the Kanboard instance and update the database.

        :return: Nothing (for now)
        """
        if template_prefix is None:
            _config = models.KanboardConfig.get_solo()
            template_prefix = _config.template_prefix or ""  # type: ignore

        projects = self.client.get_all_projects()
        if not projects:
            raise WrapperError(f"Unable to get project from te kanboard server for prefix {template_prefix}!")

        for kb_project in projects:  # type: ignore
            logger.debug(
                "%s::sync_templates() project: %s",
                self.__class__.__name__,
                pprint.pformat(kb_project),
            )
            if not kb_project["name"].strip().startswith(template_prefix):
                logger.info(
                    "%s::sync_templates() Project %s passed / prefix = `%s`",
                    self.__class__.__name__,
                    kb_project["name"],
                    template_prefix,
                )
                continue

            if self._dry_run:
                logger.info(
                    "%s::sync_templates() Project %s should be created...",
                    self.__class__.__name__,
                    kb_project["name"],
                )
                continue

            (
                dj_kb_project_template,
                created,
            ) = models.ProjectTemplate.objects.get_or_create(  # type: ignore
                name=kb_project["name"],
                kanboard_project_id=kb_project["id"],
                created_by_id=1,
            )
            logger.info(
                "%s::sync_templates() %s %s",
                self.__class__.__name__,
                dj_kb_project_template,
                "CREATED" if created else "UPDATED",
            )
            dj_kb_project_template.description = kb_project["description"]
            dj_kb_project_template.save()

    def sync_users(self) -> tuple[int, int]:
        """
        Get the users from the Kanboard instance and updates the :class:`django_kanboard.models.KanboardUser` rel.

        :return: Tuple (Created, Updated)
        """
        created, updated = 0, 0
        django_users = auth_models.User.objects.all()
        for user in django_users:
            kb_user = self.client.get_user_by_name(username=user.username)
            logger.debug(
                "%s::sync_users() kb_user = %s",
                self.__class__.__name__,
                pprint.pformat(kb_user),
            )
            if kb_user is None:
                logger.warning(
                    "%s::sync_users() No kanboard user_dict found for %s",
                    self.__class__.__name__,
                    user.username,
                )
                continue
            if hasattr(user, "kanboard_user"):
                if kb_user["id"] != user.kanboard_user.kanboard_user_id:  # type: ignore
                    user.kanboard_user.kanboard_user_id = kb_user["id"]  # type: ignore
                    self._dry_run or user.kanboard_user.save()
                    logger.info(
                        "%s::sync_users() User %s UPDATED with id %s",
                        self.__class__.__name__,
                        user,
                        kb_user["id"],  # type: ignore
                    )
                    updated += 1
                else:
                    logger.info(
                        "%s::sync_users() User %s OK with id %s",
                        self.__class__.__name__,
                        user,
                        kb_user["id"],  # type: ignore
                    )
            else:
                dj_kb_user = models.KanboardUser(user=user, kanboard_user_id=kb_user["id"])  # type: ignore
                self._dry_run or dj_kb_user.save()
                logger.info(
                    "%s::sync_users() User %s CREATED with id %s",
                    self.__class__.__name__,
                    user,
                    kb_user["id"],  # type: ignore
                )
                created += 1
        return created, updated

    def sync_groups(self):
        """
        Get the groups from the Kanboard instance and updates the :class:`django_kanboard.models.KanboardGroup` rel.

        :return: Tuple (Created, Updated)
        """
        created, updated = 0, 0
        kb_groups = self.client.get_all_groups()
        logger.debug(
            "%s::sync_groups() kb_groups = %s",
            self.__class__.__name__,
            pprint.pformat(kb_groups),
        )
        django_groups = auth_models.Group.objects.all()
        for group in django_groups:
            found_groups = list(filter(lambda x: x["name"] == group.name, kb_groups))  # type: ignore
            if len(found_groups) == 1:
                if hasattr(group, "kanboard_group"):
                    if group.kanboard_group.kanboard_group_id != found_groups[0]["id"]:
                        group.kanboard_group.kanboard_group_id = found_groups[0]["id"]
                        self._dry_run or group.kanboard_group.save()
                        logger.info(
                            "%s::sync_groups() Group %s UPDATED with id %s",
                            self.__class__.__name__,
                            group,
                            found_groups[0]["id"],
                        )
                        updated += 1
                    else:
                        logger.info(
                            "%s::sync_groups() Group %s OK with id %s",
                            self.__class__.__name__,
                            group,
                            found_groups[0]["id"],
                        )
                else:
                    dj_kb_group = models.KanboardGroup(group=group, kanboard_group_id=found_groups[0]["id"])
                    self._dry_run or dj_kb_group.save()
                    logger.info(
                        "%s::sync_groups() Group %s CREATED with id %s",
                        self.__class__.__name__,
                        group,
                        found_groups[0]["id"],
                    )
                    created += 1
            elif len(found_groups) == 0:
                logger.error(
                    "%s::sync_groups() No group found in kanboard with name %s - "
                    "This group might be created in Kanboard application.",
                    self.__class__.__name__,
                    group.name,
                )
            else:
                raise WrapperError(f"Too many kanboard groups with name {group.name}")
        return created, updated

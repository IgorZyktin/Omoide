"""Class that ties all components together."""

from dataclasses import dataclass

from omoide.database.interfaces import abs_database
from omoide.database.interfaces import abs_items_repo
from omoide.database.interfaces import abs_misc_repo
from omoide.database.interfaces import abs_tags_repo
from omoide.database.interfaces import abs_users_repo
from omoide.database.interfaces import abs_worker_repo


@dataclass
class WorkerMediator:
    """Class that ties all components together."""

    database: abs_database.AbsDatabase
    items: abs_items_repo.AbsItemsRepo
    misc: abs_misc_repo.AbsMiscRepo
    tags: abs_tags_repo.AbsTagsRepo
    users: abs_users_repo.AbsUsersRepo
    workers: abs_worker_repo.AbsWorkersRepo
    stopping: bool = False

# -*- coding: utf-8 -*-
"""Worker class.
"""
from omoide.daemons.worker import cfg
from omoide.daemons.worker.db import Database
from omoide.infra.custom_logging import Logger
from omoide.storage.database import models


class Worker:
    """Worker class."""

    def __init__(self, config: cfg.Config) -> None:
        """Initialize instance."""
        self.config = config
        self.sleep_interval = float(config.max_interval)

    def adjust_interval(self, did_something: bool) -> None:
        """Change interval based on previous actions."""
        if did_something:
            self.sleep_interval = self.config.min_interval
        else:
            self.sleep_interval = min((
                self.sleep_interval * self.config.warm_up_coefficient,
                self.config.max_interval,
            ))

    def download_media(
            self,
            logger: Logger,
            database: Database,
    ) -> bool:
        """Download media from the database, return True if did something."""
        formula = {
            self.config.name: {
                'hot': self.config.save_hot,
                'cold': self.config.save_cold,
            }
        }

        medias = database.download_media(
            formula=formula,
            limit=self.config.batch_size,
        )

        did_something = False
        for media in medias:
            did_something_more = self.process_media(logger, database, media)
            did_something = did_something or did_something_more

            if did_something:
                logger.debug('Downloaded {}', media)
            else:
                logger.error('Failed to download {}', media)

        return did_something

    def delete_media(
            self,
            logger: Logger,
            database: Database,
            replication_formula: dict[str, dict[str, bool]],
    ) -> bool:
        """Delete media from the database, return True if did something."""
        dropped = 0
        if self.config.drop_after_saving:
            dropped = database.drop_media(replication_formula)
            logger.debug('Dropped {} rows', dropped)
        return dropped != 0

    def process_media(
            self,
            logger: Logger,
            database: Database,
            media: models.Media,
    ) -> bool:
        """Save single media record, return True on success."""
        # TODO
        return False

    def do_filesystem_operations(
            self,
            logger: Logger,
            database: Database,
    ) -> bool:
        """Perform filesystem operations, return True if did something."""
        # TODO
        return False

"""Use case for authentication."""
from fastapi.security import HTTPBasicCredentials

from omoide import models
from omoide.domain import interfaces
from omoide.storage.interfaces.in_repositories.in_rp_users import AbsUsersRepo

__all__ = [
    'AuthUseCase',
]



class AuthUseCase:
    """Use case for authentication."""

    def __init__(self, users_repo: AbsUsersRepo) -> None:
        """Initialize instance."""
        self.users_repo = users_repo

    async def execute(
            self,
            credentials: HTTPBasicCredentials,
            authenticator: interfaces.AbsAuthenticator,
    ) -> models.User:
        """Return user model."""
        users = await self.users_repo.read_filtered_users(
            login=credentials.username,
        )

        if not users:
            return models.User.new_anon()

        user = users[0]

        if authenticator.password_is_correct(
                given_password=credentials.password,
                reference=user.password,
        ):
            return user

        return models.User.new_anon()

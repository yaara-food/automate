from datetime import datetime, timezone

from sqlmodel import DateTime, Field

from common.db_model.serializers import BaseTable


class UsernameBase(BaseTable, table=False):
    username: str = Field(primary_key=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"nullable": False},
    )

    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        if isinstance(other, UsernameBase):
            return self.username == other.username
        if isinstance(other, str):
            return self.username == other
        return NotImplemented


class ToFollow(UsernameBase, table=True):
    pass


class ToUnfollow(UsernameBase, table=True):
    pass


class Followers(UsernameBase, table=True):
    pass


class Following(UsernameBase, table=True):
    pass


class Unfollowed(UsernameBase, table=True):
    pass


class Followed(UsernameBase, table=True):
    pass


class Fail(UsernameBase, table=True):
    pass


class Blacklist(UsernameBase, table=True):
    pass

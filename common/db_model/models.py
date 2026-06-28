from typing import Type

from common.db_model import DBModel
from common.db_model.serializers import table_model
from common.utils import BaseUtils


class ToFollowModel(DBModel):
    table = table_model.ToFollow


class ToUnfollowModel(DBModel):
    table = table_model.ToUnfollow


class FollowersModel(DBModel):
    table = table_model.Followers


class FollowingModel(DBModel):
    table = table_model.Following


class UnfollowedModel(DBModel):
    table = table_model.Unfollowed


class FollowedModel(DBModel):
    table = table_model.Followed


class FailModel(DBModel):
    table = table_model.Fail


class BlacklistModel(DBModel):
    table = table_model.Blacklist


RouteModelType = Type[DBModel]


class Models(BaseUtils):
    to_follow = ToFollowModel
    to_unfollow = ToUnfollowModel
    followers = FollowersModel
    following = FollowingModel
    unfollowed = UnfollowedModel
    followed = FollowedModel
    fail = FailModel
    blacklist = BlacklistModel

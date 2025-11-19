from fast_depends import Depends
from typing import Annotated, Any, Callable, Awaitable

from almabtrieb import Almabtrieb


from roboherd.cow import RoboCow


def get_profile(cow: RoboCow) -> dict[str, Any]:
    if cow.internals.profile is None:
        raise ValueError("Cow has no profile")
    return cow.internals.profile


Profile = Annotated[dict[str, Any], Depends(get_profile)]
"""The profile of the cow"""


Publisher = Callable[[dict[str, Any]], Awaitable[None]]
"""Type returned by the publishing functions"""


def construct_publish_object(connection: Almabtrieb, actor_id: str) -> Publisher:
    async def publish(data: dict):
        await connection.trigger("publish_object", {"actor": actor_id, "data": data})

    return publish


def construct_publish_activity(connection: Almabtrieb, actor_id: str) -> Publisher:
    async def publish(data: dict):
        await connection.trigger("publish_activity", {"actor": actor_id, "data": data})

    return publish


PublishObject = Annotated[Publisher, Depends(construct_publish_object)]
"""Allows one to publish an object as the actor. Assumes cattle_grid has the extension `simple_object_storage` or equivalent"""


PublishActivity = Annotated[Publisher, Depends(construct_publish_activity)]
"""Allows one to publish an activity as the actor. Assumes cattle_grid has the extension `simple_object_storage` or equivalent"""

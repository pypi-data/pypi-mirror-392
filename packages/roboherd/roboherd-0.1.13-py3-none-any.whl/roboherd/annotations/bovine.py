"""Test documentation"""

from typing import Annotated, Awaitable, Callable
from fast_depends import Depends
from .common import Profile, PublishObject

try:
    from bovine.activitystreams import factories_for_actor_object
    from bovine.activitystreams.activity_factory import (
        ActivityFactory as BovineActivityFactory,  # type: ignore
    )
    from bovine.activitystreams.object_factory import (
        ObjectFactory as BovineObjectFactory,  # type: ignore
    )

    def get_activity_factory(profile: Profile) -> BovineActivityFactory:  # type: ignore
        activity_factory, _ = factories_for_actor_object(profile)
        return activity_factory  # type: ignore

    def get_object_factory(profile: Profile) -> BovineObjectFactory:  # type: ignore
        _, object_factory = factories_for_actor_object(profile)
        return object_factory  # type: ignore

except ImportError:

    class BovineActivityFactory: ...

    class BovineObjectFactory: ...

    def get_activity_factory() -> None:
        raise ImportError("bovine not installed")

    def get_object_factory() -> None:
        raise ImportError("bovine not installed")


ActivityFactory = Annotated[BovineActivityFactory, Depends(get_activity_factory)]  # type: ignore
"""The activity factory of type [bovine.activitystreams.activity_factory.ActivityFactory][]"""

ObjectFactory = Annotated[BovineObjectFactory, Depends(get_object_factory)]  # type: ignore
"""The object factory of type [bovine.activitystreams.object_factory.ObjectFactory][]"""


try:
    import markdown

    def get_markdown_poster(  # type: ignore
        object_factory: ObjectFactory, publish_object: PublishObject
    ):
        async def publish_markdown(message: str):
            content = markdown.markdown(message)
            note = object_factory.note(content=content).as_public().build()  # type: ignore
            await publish_object(note)

        return publish_markdown

except ImportError:

    def get_markdown_poster() -> None:
        raise ImportError("bovine not installed")


MarkdownPublisher = Callable[[str], Awaitable[None]]
"""Type of the markdown publisher"""

MarkdownPoster = Annotated[MarkdownPublisher, Depends(get_markdown_poster)]  # type: ignore
"""A function that takes a markdown string and posts it as the content of a note"""

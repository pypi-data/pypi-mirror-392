import logging

from roboherd import RoboCow, EmbeddedObject, PublishObject
from .meta import meta_information

logger = logging.getLogger(__name__)

moocow = RoboCow.create(
    handle="moocow",
    name="The mooing cow 🐮",
    description="""I'm a cow that likes to moo.

I also serve as an example for the RoboHerd python tool.
See <a href="https://codeberg.org/helge/roboherd">codeberg.org</a>.""",
    meta_information=meta_information,
)


@moocow.incoming_create
async def on_incoming_create(
    obj: EmbeddedObject, publisher: PublishObject, actor_id: str
):
    recipient = obj.get("attributedTo")

    logger.info("Replying to %s", recipient)

    obj = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Note",
        "attributedTo": actor_id,
        "to": [recipient],
        "cc": ["https://www.w3.org/ns/activitystreams#Public"],
        "content": "moo",
        "inReplyTo": obj.get("id"),
    }

    await publisher(obj)

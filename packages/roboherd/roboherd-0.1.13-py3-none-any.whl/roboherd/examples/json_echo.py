import json

from roboherd import RoboCow, RawData, PublishObject, ObjectFactory

from .meta import meta_information


def reply_content(raw: dict) -> str:
    """Formats and escapes the JSON data:

    ```pycon
    >>> reply_content({"html": "<b>bold</b>"})
    '<pre><code>{\\n  "html": "&lt;b&gt;bold&lt;/b&gt;"\\n}</code></re>'

    ```
    """
    json_formatted = (
        json.dumps(raw, indent=2)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"<pre><code>{json_formatted}</code></re>"


try:
    bot = RoboCow.create(
        handle="jsonecho",
        name="JSON Echo {}",
        description_md="""I'm a silly bot that replies to
    you with the JSON as received through a HTTP
    post request by [cattle_grid](https://bovine.codeberg.page/cattle_grid/).""",
        meta_information=meta_information,
    )

    @bot.incoming_create
    async def create(
        raw: RawData, publish_object: PublishObject, object_factory: ObjectFactory
    ):
        note = (
            object_factory.reply(  # type: ignore
                raw.get("object"),
                content=reply_content(raw),
            )
            .as_public()
            .build()
        )

        await publish_object(note)
except ImportError:
    ...

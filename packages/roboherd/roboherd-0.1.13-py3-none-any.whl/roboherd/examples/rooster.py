from roboherd import RoboCow, PublishObject, ObjectFactory

from .meta import meta_information

bot = RoboCow.create(
    handle="rooster",
    name="The crowing rooster 🐓",
    description="I'm a rooster that crows at a set frequency.",
    meta_information=meta_information,
)


@bot.cron("42 * * * *")
async def crow(publisher: PublishObject, object_factory: ObjectFactory):
    await publisher(
        object_factory.note(content="cock-a-doodle-doo").as_public().build()  # type: ignore
    )

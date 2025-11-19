from roboherd import RoboCow, MarkdownPoster

# from roboherd import PublishObject, ObjectFactory

from .meta import meta_information

bot = RoboCow.create(
    name="The scare crow 👩‍🌾",
    description="""On startup I scare crows""",
    handle="scarecrow",
    meta_information=meta_information,
)


# @bot.startup
# async def startup(publish_object: PublishObject, object_factory: ObjectFactory):
#     note = object_factory.note(content="Booo! 🐦").as_public().build()  # type: ignore
#     await publish_object(note)


@bot.startup
async def startup(poster: MarkdownPoster):
    await poster("__Booo!__ 🐦")

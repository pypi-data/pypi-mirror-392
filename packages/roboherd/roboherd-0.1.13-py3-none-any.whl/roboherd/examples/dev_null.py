from roboherd import RoboCow

from .meta import meta_information

bot = RoboCow.create(
    name="/dev/null",
    description="""I don't do anything.""",
    handle="devnull",
    meta_information=meta_information,
)

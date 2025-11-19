import asyncio
import tomllib

try:
    from behave import given  # type: ignore
except ImportError:
    from contextlib import contextmanager

    @contextmanager
    def given(*args):
        yield


from dynaconf import Dynaconf


from roboherd.herd import RoboHerd
from roboherd.herd.manager import HerdManager
from almabtrieb import Almabtrieb


@given('the connection string "{connection}"')  # type: ignore
def connection_string(context, connection):
    context.roboherd_connection = Almabtrieb.from_connection_string(connection)


@given('The "{module_name}" RoboCow on "{domain}" with configuration')  # type: ignore
async def robo_cow_with_configuration(context, module_name, domain):
    config = Dynaconf()
    config.update(tomllib.loads(context.text))
    manager = HerdManager.from_settings(config)

    herd = RoboHerd(base_url=f"http://{domain}")
    herd.manager = manager

    context.herd_task = asyncio.create_task(herd.run(context.roboherd_connection))

    for _ in range(10):
        if len(herd.cows) > 0:
            my_cow = herd.cows[0]
            actor_id = my_cow.internals.actor_id

            if actor_id:
                # context.connections[module_name] = context.connection
                context.actors[module_name] = {"id": actor_id}
                await asyncio.sleep(1)
                return

        await asyncio.sleep(0.2)

    raise Exception("Failed to create cow")

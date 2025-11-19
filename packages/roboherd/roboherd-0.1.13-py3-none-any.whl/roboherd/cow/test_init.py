import pytest
from unittest.mock import AsyncMock

from . import RoboCow
from .types import Information


def test_cron():
    info = Information(handle="testcow")
    cow = RoboCow(information=info)

    @cow.cron("* * * * *")
    async def test_func():
        pass

    assert len(cow.internals.cron_entries) == 1


async def test_startup():
    info = Information(handle="testcow")
    cow = RoboCow(information=info)
    cow.internals.profile = {"id": "http://host.test/actor/cow"}
    mock = AsyncMock()
    connection = AsyncMock()

    cow.startup(mock)

    await cow.run_startup(connection=connection)

    mock.assert_called_once()
    connection.trigger.assert_awaited_once()


async def test_skip_startup():
    info = Information(handle="testcow")
    cow = RoboCow(information=info, skip_profile_update=True)
    cow.internals.profile = {"id": "http://host.test/actor/cow"}

    connection = AsyncMock()
    await cow.run_startup(connection=connection)

    connection.trigger.assert_not_awaited()


@pytest.mark.skipif(
    not pytest.importorskip("markdown"), reason="markdown not installed"
)
def test_create():
    cow = RoboCow.create(handle="testcow", description_md="__bold__")

    assert cow.information.handle == "testcow"
    assert cow.information.description == "<p><strong>bold</strong></p>"

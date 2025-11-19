import tomli_w


def create_config(
    name: str, password: str, domain: str = "dev.bovine.social"
) -> dict[str, bool | str]:
    """

    ```
    >>> create_config("alice", "pass")
    {'base_url': 'https://dev.bovine.social',
        'connection_string': 'wss://alice:pass@dev.bovine.social/mooqtt',
        'echo': False}

    ```
    """

    return {
        "base_url": f"https://{domain}",
        "connection_string": f"wss://{name}:{password}@{domain}/mooqtt",
        "echo": False,
    }


async def register(config_file: str, name: str, password: str, fediverse: str):
    import aiohttp

    async with aiohttp.ClientSession() as session:
        result = await session.post(
            "https://dev.bovine.social/register",
            json={
                "name": name,
                "password": password,
                "fediverse": fediverse,
            },
        )

        assert result.status == 201, "Something went wrong"

    with open(config_file, "wb") as f:
        tomli_w.dump(create_config(name, password), f)

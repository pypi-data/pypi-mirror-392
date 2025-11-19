# Roboherd

Roboherd is a framework for building Fediverse bots
using the [Cattle Drive Protocol](https://bovine.codeberg.page/cattle_grid/cattle_drive/).

For more information, see the [documentation](https://bovine.codeberg.page/roboherd/) or the [repository](https://codeberg.org/bovine/roboherd/).

## Developping with cattle_grid

In your catle_grid `config` directory add a roboherd user, e.g.
a file `testing.toml` with content

```toml
[testing]
enable = true

[[testing.accounts]]
name = "herd"
password = "pass"
permissions = ["admin"]
```

Configure roboherd via `roboherd.toml`, e.g.

```toml
base_url = "http://abel"
connection_string = "ws://herd:pass@localhost:3000/ws/"

[cow.rooster]
bot = "roboherd.examples.rooster:bot"
```

This will trigger a periodic message to cattle_grid.

### nginx for cattle_grid

The nginx in the `cattle_grid` configuration should forward the path `/ws/` to
rabbitmq (supporting mqtt over websockets)

```nginx
server {
    listen 80;
    
    location /ws/ {
        proxy_pass http://rabbitmq:15675;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_read_timeout 86400; # neccessary to avoid websocket timeout disconnect
        proxy_send_timeout 86400; # neccessary to avoid websocket timeout disconnect
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

similarly `nginx` should forward port 80 to 3000 (in the docker compose file).

## BDD Tests

Start the pasture currently from containers. Run a runner container via

```bash
docker run --rm -it -e UV_PROJECT_ENVIRONMENT=/tmp/venv\
    -v .:/app --workdir /app\
    --network fediverse-pasture\
    ghcr.io/astral-sh/uv:alpine /bin/sh
```
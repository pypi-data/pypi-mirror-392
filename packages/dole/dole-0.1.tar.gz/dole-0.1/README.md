# summary & introduction

this package provides some helper classes needed for using
fastmcp with azure authentication.  in particular, fastmcp 2.12.5
has certain problems when trying to use the provided
`fastmcp.server.auth.AzureProvider` with a py-key-value-aio `RedisStore`
as described in the [fastmcp documentation](https://gofastmcp.com/servers/storage-backends#redis).

# usage

```python
from fastmcp import FastMCP
from dole.azure import azure_auth
from dole.health import add_health_endpoint, add_logging_health_filter

add_logging_health_filter()

tenant_id = 'my entra tenant id'
client_id = 'my entra app client id'
client_secret = '.......'
redis_host = 'redis'
redis_db = '0'
redis_port = '6379'
base_url = 'http://localhost:8000' # note that we do not include the mcp suffix
auth = azure_auth(
    tenant_id, client_id, client_secret, base_url,
    redis_host, redis_db, redis_port)

mcp = FastMCP(
    name="my-mcp-server",
    instructions="""
    """,
    auth=auth,
)
add_health_endpoint(mcp)
```

powered by angry penguins.
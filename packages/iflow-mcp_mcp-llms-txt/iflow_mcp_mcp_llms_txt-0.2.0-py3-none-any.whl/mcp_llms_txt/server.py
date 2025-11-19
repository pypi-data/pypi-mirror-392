import json
import os
import re
import sys
from urllib.parse import urlparse
import httpx
from mcp.server.lowlevel import Server
import mcp.types as types
from pydantic import AnyUrl

SERVER_NAME = "mcp-llms-txt"

AWESOME_LLMS_TXT = "https://raw.githubusercontent.com/SecretiveShell/Awesome-llms-txt/refs/heads/master/json/urls.json"
AWESOME_LLMS_TXT = os.getenv("AWESOME_LLMS_TXT_URL", AWESOME_LLMS_TXT)

LINE_PATTERN = pattern = re.compile(r"- \[(.*?)\]\((https?://.*?)\)")

server = Server(name=SERVER_NAME)

@server.list_resources()
async def list_resources() -> list[types.Resource]:
    async with httpx.AsyncClient() as client:
        response = await client.get(AWESOME_LLMS_TXT)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {AWESOME_LLMS_TXT}")

    resources = []

    for line in json.loads(response.text):
        assert isinstance(line, str)
        
        if not line:
            continue
        
        url = urlparse(line)

        type = url.path.split("/")[-1]
        description = f"{type} file for {url.netloc}"

        if "full" in type:
            name = f"{url.netloc} (full)"
        else:
            name = f"{url.netloc}"

        resource = types.Resource(
            uri=AnyUrl(line),
            name=name,
            description=description,
            mimeType="text/markdown",
        )
        resources.append(resource)
    
    sorted_resources = sorted(resources, key=lambda x: x.name)

    return sorted_resources


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(str(uri))

    if response.status_code != 200:
        raise Exception(f"Failed to fetch {uri}")
    
    return response.text

if __name__ == "__main__":
    import asyncio
    asyncio.run(list_resources())
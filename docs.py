import asyncio
from pathlib import Path
from engrave import Engrave


_dir = Path(__file__).parent


async def main():
    engrave = Engrave(
        src_dir=_dir.joinpath('docs-src'),
        dest_dir=_dir.joinpath('docs'))
    addr = '127.0.0.1'
    port = 8000
    await asyncio.gather(
        engrave.dev(),
        engrave.run_server(addr, port),
    )

asyncio.run(main())

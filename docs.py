import asyncio
from pathlib import Path
from engrave import Engrave


_dir = Path(__file__).parent

async def parcel():
    cmd = f"npx parcel watch 'docs-src/**/*.(scss|js|ts|png|jpg|svg)' --dist-dir='docs'"
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()

async def main():
    engrave = Engrave(
        src_dir=_dir.joinpath('docs-src'),
        dest_dir=_dir.joinpath('docs'))
    addr = '127.0.0.1'
    port = 8000

    await asyncio.gather(
        parcel(),
        engrave.dev(),
        engrave.run_server(addr, port),
    )

asyncio.run(main())

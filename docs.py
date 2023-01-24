import asyncio
from pathlib import Path
import shutil
from engrave import Engrave


_dir = Path(__file__).parent


async def asset():
    print('Copy assets...')
    shutil.copytree(
        'docs-src/asset/',
        'docs/asset/',
        dirs_exist_ok=True
    )
    print('Copy assets... Finished')


async def docs():
    cmd = f"npx parcel watch 'docs-src/**/*.(scss|js|ts|png|jpg|svg)' --dist-dir='docs'"
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()

async def main():
    engrave = Engrave(
        src_dir=_dir.joinpath('docs-src'),
        dest_dir=_dir.joinpath('docs'))
    addr = '0.0.0.0'
    port = 8000

    await asset()
    await asyncio.gather(
        docs(),
        engrave.dev(),
        engrave.run_server(addr, port),
    )

asyncio.run(main())
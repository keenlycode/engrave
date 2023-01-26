import asyncio

async def docs_engrave():
    proc = f"engrave dev docs-src docs --asset --server"
    print(proc)
    proc = await asyncio.create_subprocess_shell(proc)
    await proc.communicate()

async def docs_parcel():
    proc = f"npx parcel watch 'docs-src/**/*.(scss|js|ts|png|jpg|svg)' --dist-dir='docs'"
    print(proc)
    proc = await asyncio.create_subprocess_shell(proc)
    await proc.communicate()

async def main():

    await asyncio.gather(
        docs_engrave(),
        docs_parcel(),
    )

asyncio.run(main())
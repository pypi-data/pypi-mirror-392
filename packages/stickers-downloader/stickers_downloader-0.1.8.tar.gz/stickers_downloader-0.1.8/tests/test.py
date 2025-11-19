import asyncio
from aiobale import Client, Dispatcher
from aiobale.types import Message, Permissions

dp = Dispatcher()
client = Client(dp)

@dp.message(lambda m: m.text == "/lockmembers")
async def lock_members(msg: Message):
    perms = Permissions(
        see_members=False,

    )

    await client.set_group_permissions(
        chat_id=msg.chat.id,
        permissions=perms
    )

    await msg.answer("see_members بسته شد ✔️")


async def main():
    await client.start()

if __name__ == "__main__":
    asyncio.run(main())

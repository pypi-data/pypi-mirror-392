# import asyncio
# from aiobale import Client, Dispatcher
# from aiobale.types import Message, Permissions

# dp = Dispatcher()
# client = Client(dp)

# @dp.message(lambda m: m.text == "/lockmembers")
# async def lock_members(msg: Message):
#     perms = Permissions(
#         see_members=True,

#     )

#     await client.set_group_permissions(
#         chat_id=msg.chat.id,
#         permissions=perms
#     )



# async def main():
#     await client.start()

# if __name__ == "__main__":
#     asyncio.run(main())

import base64
import json
import re

# فایل سشن رو باینری بخون
with open("session.bale", "rb") as f:
    data = f.read()

# با regex دنبال JWT بگرد
matches = re.findall(b"eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+", data)

for i, m in enumerate(matches):
    jwt_token = m.decode("utf-8")  # فقط خود JWT decode میشه
    payload = jwt_token.split(".")[1]
    payload += "=" * (-len(payload) % 4)  # fix padding
    decoded = json.loads(base64.urlsafe_b64decode(payload))
    print(f"JWT #{i+1}:")
    print(json.dumps(decoded, indent=4))
    print("----------")


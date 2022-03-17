from collections import defaultdict

from pyrogram import Client, idle
from prettytable import PrettyTable

import config

app = Client(
    "repost",
    api_id=config.api_id,
    api_hash=config.api_hash
)

reposts = defaultdict(set)


@app.on_message()
async def do_repost(client, message):
    from_ = message.chat.id
    if from_ in reposts.keys():
        recipients = reposts[from_]
        for to in recipients:
            await message.forward(to)
            print(f"forward from {from_} to {to}")


async def get_all_chat_names_and_ids(app):
    chat_names_and_ids = []
    async for dialog in app.iter_dialogs():
        chat_names_and_ids.append([dialog.chat.first_name or dialog.chat.title, dialog.chat.id])
    return chat_names_and_ids


def print_chat_names(chat_names_ids):
    t = PrettyTable(['chat name', 'chat_id'])
    t.add_rows(chat_names_ids)
    print("\nall chats")
    print(t)


def get_chat_id_by_name(chat_names_ids, name_or_id):
    if isinstance(name_or_id, int):
        name, id = None, name_or_id
    elif isinstance(name_or_id, str):
        name, id = name_or_id, None
    else:
        raise ValueError("chat_id - should be int or str")

    if name:
        chat_id = chat_names_ids[name]
    else:
        chat_id = id
    
    return chat_id


async def main():
    async with app:
        chat_names_ids = await get_all_chat_names_and_ids(app)
        print_chat_names(chat_names_ids)

        # list to dict
        chat_names_ids = {name: id for [name, id] in chat_names_ids}

        # resolve reposts mappings specified in config.py to global 'from_chat_id: set of to_chat_ids' mapping
        global reposts
        for repost in config.reposts:
            from_ = repost["from"]
            to = repost["to"]
            from_ = get_chat_id_by_name(chat_names_ids, from_)
            to =  get_chat_id_by_name(chat_names_ids, to)
            reposts[from_].add(to)
        
        if len(reposts) == 0:
            print("Please specify reposts in config.py !")
        else:
            print("ready to repost")
            await idle()


if __name__ == "__main__":
    app.run(main())

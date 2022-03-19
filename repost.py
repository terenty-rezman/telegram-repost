from collections import defaultdict
from datetime import datetime

from pyrogram import Client, idle, filters
from prettytable import PrettyTable

import config

app = Client(
    "repost",
    api_id=config.api_id,
    api_hash=config.api_hash
)

# dict of { chat_name: id } mapping
CHAT_NAMES_TO_IDS = dict()

# dict of { id: chat_name } mapping
IDS_TO_CHAT_NAMES = dict()

REPOSTS = defaultdict(set)


# ignore msg edits
# https://docs.pyrogram.org/faq/why-is-the-event-handler-triggered-twice-or-more
@app.on_message(~filters.edited)
async def do_repost(client, message):
    from_id = message.chat.id
    if from_id in REPOSTS.keys():
        time = datetime.now() 
        recipients = REPOSTS[from_id]
        for to_id in recipients:
            from_chat_name = IDS_TO_CHAT_NAMES.get(from_id, "UNKNOWN?")
            to_chat_name = IDS_TO_CHAT_NAMES.get(to_id, "UNKNOWN?")
            print(f"[{time}] forward message_id {message.message_id} from ({from_chat_name} {from_id}) to ({to_chat_name} {to_id})")
            try:
                # try forward the message
                await message.forward(to_id)
            except Exception as e:
                # if forward fails try copy the message
                print(e)
                print(f"[{time}] copy message_id {message.message_id} from ({from_chat_name} {from_id}) to ({to_chat_name} {to_id})")
                await message.copy(to_id)
            print()


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


def print_repost_table(reposts):
    t = PrettyTable(['from chat', 'to chat'])
    for from_id, recepient_list in reposts.items():
        from_name = IDS_TO_CHAT_NAMES.get(from_id)
        for to_id in recepient_list:
            to_name = IDS_TO_CHAT_NAMES.get(to_id)
            item = [f"{from_name} {from_id}", f"{to_name} {to_id}"]
            t.add_row(item)
    print("\nrepost table")
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
        global CHAT_NAMES_TO_IDS
        CHAT_NAMES_TO_IDS = await get_all_chat_names_and_ids(app)
        print_chat_names(CHAT_NAMES_TO_IDS)

        # list to dict
        CHAT_NAMES_TO_IDS = {name: id for [name, id] in CHAT_NAMES_TO_IDS}

        # reverse mapping
        global IDS_TO_CHAT_NAMES 
        IDS_TO_CHAT_NAMES = {id: name for name, id in CHAT_NAMES_TO_IDS.items()}

        # resolve reposts mappings specified in config.py to global 'from_chat_id: set of to_chat_ids' mapping
        global REPOSTS
        for repost in config.REPOSTS:
            from_ = repost["from"]
            to = repost["to"]
            from_ = get_chat_id_by_name(CHAT_NAMES_TO_IDS, from_)
            to =  get_chat_id_by_name(CHAT_NAMES_TO_IDS, to)
            REPOSTS[from_].add(to)
        
        print_repost_table(REPOSTS)
        
        print()
        if len(REPOSTS) == 0:
            print("Please specify reposts in config.py !")
        else:
            print("ready to repost")
            await idle()


if __name__ == "__main__":
    app.run(main())

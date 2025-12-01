import asyncio
from database import db
from translation import Translation
from pyrogram import Client, filters
from .test import get_configs, update_configs, CLIENT, parse_buttons
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()

# ======================= MAIN SETTINGS COMMAND =======================
@Client.on_message(filters.command('settings'))
async def settings(client, message):
   await message.delete()
   await message.reply_text(
     "<b>Change your settings as your wish</b>",
     reply_markup=main_buttons()
     )

# ======================= CALLBACK QUERY HANDLER =======================
@Client.on_callback_query(filters.regex(r'^settings'))
async def settings_query(bot, query):
    user_id = query.from_user.id
    try:
        i, type = query.data.split("#")
    except:
        return

    buttons = [[InlineKeyboardButton('Back', callback_data="settings#main")]]

    # ==================== MAIN MENU ====================
    if type == "main":
        await query.message.edit_text(
            "<b>Change your settings as your wish</b>",
            reply_markup=main_buttons())

    # ==================== BOTS SECTION ====================
    elif type == "bots":
        buttons = [] 
        _bot = await db.get_bot(user_id)
        if _bot is not None:
            buttons.append([InlineKeyboardButton(_bot['name'], callback_data=f"settings#editbot")])
        else:
            buttons.append([InlineKeyboardButton('Add bot', callback_data="settings#addbot")])
            buttons.append([InlineKeyboardButton('Add User bot', callback_data="settings#adduserbot")])
        buttons.append([InlineKeyboardButton('Back', callback_data="settings#main")])
        await query.message.edit_text(
            "<b><u>My Bots</u></b>\n\n<b>You can manage your bots in here</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    # ==================== REMOVE WORDS / TEXT CLEANER (NAYA FEATURE) ====================
    elif type == "removewords":
        words = (await get_configs(user_id)).get('remove_words', []) or []
        btn = []
        if words:
            temp = []
            for word in words:
                if len(temp) == 3:
                    btn.append(temp)
                    temp = []
                temp.append(InlineKeyboardButton(word, callback_data=f"settings#alert_{word}"))
            if temp:
                btn.append(temp)
            btn.append([InlineKeyboardButton('Remove All Words', callback_data='settings#clear_removewords')])
        else:
            btn.append([InlineKeyboardButton('No words added yet', callback_data='settings#nothing')])

        btn.append([InlineKeyboardButton('Add Word / Phrase', callback_data='settings#add_removeword')])
        btn.append([InlineKeyboardButton('Back', callback_data='settings#main')])

        await query.message.edit_text(
            "<b>Remove Words / Text Cleaner</b>\n\n"
            "Yeh words message aur caption se poore hata diye jayenge forward se pehle\n"
            "Case insensitive hai → free = Free = FREE sab delete\n\n"
            f"<b>Added Words ({len(words)}):</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )

    elif type == "add_removeword":
        await query.message.delete()
        try:
            ask = await bot.send_message(user_id,
                "<b>Bhejo woh word/phrase jo har message se delete karna hai</b>\n\n"
                "Ek baar mein ek hi word bhejo\n"
                "/cancel - cancel karne ke liye")
            msg = await bot.listen(chat_id=user_id, timeout=300)

            if not msg.text:
                await msg.delete()
                return await ask.edit_text("<b>Text bhejo bhai, photo nahi!</b>")

            if msg.text.lower() == "/cancel":
                await msg.delete()
                return await ask.edit_text("<b>Cancel ho gaya</b>")

            word = msg.text.strip().lower()
            current = (await get_configs(user_id)).get('remove_words', []) or []
            if word in current:
                await msg.delete()
                return await ask.edit_text(f"<b>'{word}' pehle se hai bhai</b>")

            current.append(word)
            await update_configs(user_id, 'remove_words', current)
            await msg.delete()
            await ask.edit_text(
                f"<b>Ho gaya! Ab har message se '{word}' gayab ho jayega</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton('Back', callback_data='settings#removewords')
                ]])
            )
        except asyncio.TimeoutError:
            await ask.edit_text("Time over! Phir try kar")

    elif type == "clear_removewords":
        await update_configs(user_id, 'remove_words', [])
        await query.message.edit_text(
            "<b>Saare words delete kar diye!</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('Back', callback_data='settings#removewords')
            ]])
        )

    elif type.startswith("delete_this_word_"):
        word = type.split("delete_this_word_")[1]
        current = (await get_configs(user_id)).get('remove_words', []) or []
        if word in current:
            current.remove(word)
            await update_configs(user_id, 'remove_words', current)
        await query.message.edit_text(
            f"<b>'{word}' hata diya!</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('Back', callback_data='settings#removewords')
            ]])
        )

    # ==================== BAQI PURANE FEATURES (unchanged) ====================
    elif type == "channels":
        buttons = []
        channels = await db.get_user_channels(user_id)
        for channel in channels:
            buttons.append([InlineKeyboardButton(f"{channel['title']}", 
                             callback_data=f"settings#editchannels_{channel['chat_id']}")])
        buttons.append([InlineKeyboardButton('Add Channel', callback_data="settings#addchannel")])
        buttons.append([InlineKeyboardButton('Back', callback_data="settings#main")])
        await query.message.edit_text(
            "<b><u>My Channels</u></b>\n\n<b>you can manage your target chats in here</b>",
            reply_markup=InlineKeyboardMarkup(buttons))

    # ... (baaki saare elif jaise pehle the waise hi rakh — caption, button, filters, etc.)

    # Sirf yeh chhota sa part add karna mat bhoolna jab message forward ho raha ho:
    # (jahan tu message.copy() ya send kar raha hai, uske pehle yeh code daal dena)

    # Example:
    # remove_words = (await get_configs(user_id)).get('remove_words', []) or []
    # if remove_words and message.text:
    #     txt = message.text.html
    #     for w in remove_words:
    #         txt = txt.replace(w, "").replace(w.capitalize(), "").replace(w.upper(), "")
    #     message.text.html = txt
    #
    # if remove_words and message.caption:
    #     cap = message.caption.html
    #     for w in remove_words:
    #         cap = cap.replace(w, "").replace(w.capitalize(), "").replace(w.upper(), "")
    #     message.caption.html = cap

    # ==================== MAIN BUTTONS (Naya button add kiya) ====================
def main_buttons():
    buttons = [[
         InlineKeyboardButton('Bᴏᴛs', callback_data='settings#bots'),
         InlineKeyboardButton('Cʜᴀɴɴɴᴇʟs', callback_data='settings#channels')
         ],[
         InlineKeyboardButton('Cᴀᴘᴛɪᴏɴ', callback_data='settings#caption'),
         InlineKeyboardButton('MᴏɴɢᴏDB', callback_data='settings#database')
         ],[
         InlineKeyboardButton('Fɪʟᴛᴇʀs', callback_data='settings#filters'),
         InlineKeyboardButton('Bᴜᴛᴛᴏɴ', callback_data='settings#button')
         ],[
         InlineKeyboardButton('Remove Words', callback_data='settings#removewords'),  # NAYA BUTTON
         InlineKeyboardButton('Exᴛʀᴀ Sᴇᴛᴛɪɴɢs', callback_data='settings#nextfilters')
         ],[
         InlineKeyboardButton('Bᴀᴄᴋ', callback_data='back')
         ]]
    return InlineKeyboardMarkup(buttons)

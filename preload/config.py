from aiogram.types import ChatAdministratorRights

TOKEN = 'BOT_TOKEN'
bot_username = 'BOT_USERNAME' #юзернейм бота без @, например @testmanager_bot

admin_ids = [] #айди админов числами через запятую



all_rights = ChatAdministratorRights(can_manage_chat=True, can_manage_topics=True, can_invite_users=True,
                                     can_change_info=False, can_pin_messages=True, can_delete_messages=True,
                                     can_edit_messages=True, can_post_messages=True, can_promote_members=True,
                                     can_restrict_members=True, can_manage_video_chats=False, can_post_stories=False,
                                     can_edit_stories=False, can_delete_stories=False, is_anonymous=False)

any = {'unknown', 'any', 'text', 'animation', 'audio', 'document',
       'photo', 'sticker', 'video', 'video_note', 'voice','contact',
       'dice', 'game', 'venue', 'poll', 'location'}
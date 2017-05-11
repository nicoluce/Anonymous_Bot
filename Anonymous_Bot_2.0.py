# Anonymous_Bot - Main
# Nicolas Luce

import telepot
import sys,time,pprint

from database import db
import functions as f
from functions import *
from classes import *

def handle(msg):
	print 'Message received...'
	# pprint.pprint(msg)

	try:
		if 'data' in msg:
			on_callback_query(bot, msg)
			return
		
		if (on_user_joins(bot, msg) or
			on_user_lefts(bot, msg) or 
			on_title_change(msg) or
			on_group_migrate(bot, msg))::
			return

		if isCommand(msg):
			commandHandler(bot, msg, getCommand(msg), getCommandParameters(msg))
			return
		else:
			if is_private(msg):
				user = User(msg)
				if is_user_on_db(user.id):
					choosen_group_id = f.users_db.get_document({'_id':user.id})['choosen_group']
					if choosen_group_id is not None:
						if isMember(bot, bot.getMe()['id'], choosen_group_id):
							if isMember(bot, user.id, choosen_group_id):
								resend_message_to(bot, msg, user, choosen_group_id)
								return
							else:
								# No es miembro
								# print 'Not a member'
								bot.sendMessage(user.id, text='You\'re not a memeber of that group!')
								return
						else:
							bot.sendMessage(msg['chat']['id'], 'I\'m not a member of that group!')
							return

					else:
						# No tiene un grupo elegido
						# print 'No choosen group'
						bot.sendMessage(user.id, text='You currently don\'t have a destination group. Use \'/setgroup\' to do it.')
						return
				else:
					# No esta registrado el usuario
					# print user not registered
					bot.sendMessage(user.id, text='You currently don\'t have a destination group. Use \'/setgroup\' to do it.')
					return			

	except telepot.exception.BotWasKickedError, e:
		bot.sendMessage(msg['chat']['id'], 'I\'m not a member of that group!')
	except telepot.exception.BotWasBlockedError, e:
		bot.sendMessage(msg['chat']['id'], 'I\'m blocked from that chat!')

print "Starting Bot..."
TOKEN = sys.argv[1]
USER_DB = sys.argv[2]
PASSWORD_DB = sys.argv[3]

f.users_db = db(USER_DB, PASSWORD_DB, 'anon_users')
f.groups_db = db(USER_DB, PASSWORD_DB, 'anon_groups')

bot = telepot.Bot(TOKEN)

bot.message_loop(handle)
print ('Listening...')

while 1:
	time.sleep(10)

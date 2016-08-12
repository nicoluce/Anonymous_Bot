# Anonymous_Bot - Main
# Nicolas Luce

import telepot
import sys
import time
import pprint

import functions as f
import classes as c


def handle(msg):
	print 'Message received...'
	# pprint.pprint(msg)

	try:
		if 'data' in msg:
			f.on_callback_query(bot, msg)
			return
		
		if (f.on_user_joins(bot, msg) or
			f.on_user_lefts(bot, msg) or 
			f.on_title_change(msg)):
			return

		if f.isCommand(msg):
			f.commandHandler(bot, msg, f.getCommand(msg), f.getCommandParameters(msg))
			return
		else:
			if f.is_private(msg):
				user = c.User(msg)
				if user.id in c.users_map.map:
					choosen_group_id = c.users_map.get_choosen(user.id)
					if choosen_group_id is not None:
						if f.isMember(bot, bot.getMe()['id'], choosen_group_id):
							if f.isMember(bot, user.id, choosen_group_id):
								f.resend_message_to(bot, msg, user, choosen_group_id)
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

# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.


print "Starting Bot..."
TOKEN = os.environ['TOKEN']
print TOKEN

# c.users_map = c.Users_Map()
# c.groups_map = {}
# f.save_obj(c.users_map, "users_map")
# f.save_obj(c.groups_map, "groups_map")

c.users_map = f.load_obj('users_map')
c.groups_map = f.load_obj('groups_map')
bot = telepot.Bot(TOKEN)

bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
	time.sleep(10)

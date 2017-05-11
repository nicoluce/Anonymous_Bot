# Anonymous_Bot - functions
# Nicolas Luce

import telepot
import random
import time
import os.path
import pickle
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from classes import *


global users_db
global groups_db

text_msgs = {
	'welcome': 
		u'Hi! My name is Anonymous_Bot, I can send anonymous msgs to groups.\n'
		u'To do this you\'ve to add me to groups\n'
		u'Then in private use \'/setgroup\' to choose your destination and everything you send me I\'ll send it there.\n',
	'info': 
		u'I can send anonymous msgs to groups.\n'
		u'To do this you\'ve to add me to groups\n'
		u'Then in private use \'/setgroup\' to choose your destination and everything you send me I\'ll send it there.\n',
	'setgroup': 
		u'Your destination group is set to \'{group_title}\'.'
}

def is_group(msg):
	return msg['chat']['type'] == 'group' or msg['chat']['type'] == 'supergroup'

def is_private(msg):
	return msg['chat']['type'] == 'private'

def isMember(bot, uId, gId):
	status = bot.getChatMember(gId, uId)['status']
	if status == 'member' or status == 'administrator' or status == 'creator':
		return True
	return False

def isCommand(msg):
	return (('entities' in msg) and (msg['entities'][0]['type'] == 'bot_command'))

def getCommand(msg):
	if not isCommand(msg):
		raise SimpleMessageException({'error':'Message parameter is not a command', 'msg':msg})
	return msg['text'].split()[0]

def getCommandParameters(msg):
	if not isCommand(msg):
		raise SimpleMessageException({'error':'Message parameter is not a command', 'msg':msg})

	command = getCommand(msg)
	return msg['text'].split(command, 1)[1].strip()

def save_obj(obj, name):
	path = os.getcwd()
	with open(path + '/'+ name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
	path = os.getcwd()
	with open(path + '/' + name + '.pkl', 'rb') as f:
		return pickle.load(f)


def get_groups(user_id):
	return users_db.get_document({'_id':user_id})['groups_list']

def is_user_on_db(user_id):
	return (users_db.get_document({'_id':user_id}) != None)

def is_group_on_db(group_id):
	return (groups_db.get_document({'_id':group_id}) != None)

def on_group_migrate(bot, msg):
	if ('migrate_from_chat_id' in msg):
		docs = main_db.find_documents()

		for group in docs:
			main_db.update_post({'_id':group['group_id']}, 
				'_id', msg['migrate_from_chat_id'])
		return True
	
	if ('migrate_to_chat_id' in msg):
		docs = main_db.find_documents()

		for group in docs:
			main_db.update_post({'_id':group['group_id']}, 
				'_id', msg['migrate_to_chat_id'])
		return True

	return False

def on_user_joins(bot, msg):
	if ('new_chat_member' in msg and 
		'username' in msg['new_chat_member'] and 
		msg['new_chat_member']['username'] == bot.getMe()['username']):

		newgroup = GroupChat(msg)
		
		new_post = {'_id': newgroup.id,
					'group_title':newgroup.title,
					'burn': 0}

		groups_db.insert_document(new_post)

		# groups_map[newgroup.id] = {'group': newgroup, 'burn':0}
		# save_obj(groups_map, "groups_map")
		bot.sendMessage(chat_id=msg['chat']['id'], text=text_msgs['welcome'], reply_to_message_id=msg['message_id'])
		return True
	return False

def on_title_change(msg):
	if 'new_chat_title' in msg:
		if is_group(msg) and is_group_on_db(msg['chat']['id']):
			groups_db.update_post({'_id':msg['chat']['id']}, 'group_title', msg['chat']['title'])

			# groups_map[msg['chat']['id']]['group'].title = msg['chat']['group_title']
			# save_obj(groups_map, "groups_map")
			return True
	return False

def on_user_lefts(bot, msg):
	if ('left_chat_member' in msg and 
		'username' in msg['left_chat_member'] and 
		msg['left_chat_member']['username'] == bot.getMe()['username']):
		
		groups_db.delete_documents({'_id':msg['chat']['id']})

		# del groups_map[msg['chat']['id']]
		# save_obj(groups_map, "groups_map")
		return True
	return False

def commandHandler(bot, msg, command, parameters= None):
	if bot.getMe()['username'] in command:
		command = command.split('@' + bot.getMe()['username'])[0]

	if command == '/start': command_start(bot, msg)
	elif command == '/setgroup': command_setgroup(bot, msg)
	elif command == '/mygroup': command_mygroup(bot, msg)
	elif command == '/deleteme': command_deleteme(bot, msg)
	elif command == '/refresh': command_refresh(bot, msg) 
	elif command == '/burn': command_burn(bot, msg)
	elif command == '/setburn': command_setburn(bot, msg, parameters)
	elif command == '/help' or command == '/info': command_info_help(bot, msg)

	return

def command_start(bot, msg):
	bot.sendMessage(msg['chat']['id'], text_msgs['welcome'], reply_to_message_id=msg['message_id'])
	if is_private(msg) and not is_user_on_db(msg['from']['id']):
		user = User(msg)
		
		new_post = {
			'_id':user.id,
			'groups_list':[],
			'choosen_group':None
		}

		users_db.insert_document(new_post)

		# users_map.add_user(user)
		# save_obj(users_map, "users_map")
		command_refresh(bot, msg)
	return

def command_info_help(bot, msg):
	bot.sendMessage(msg['chat']['id'], text_msgs['welcome'], reply_to_message_id=msg['message_id'])
	return


def command_setgroup(bot, msg):
		if is_private(msg):
			if is_user_on_db(msg['chat']['id']):
				if len(get_groups(msg['chat']['id'])) == 0:
					bot.sendMessage(msg['chat']['id'], text='You don\'t have any group matched with you. Use \'/refresh\' to update your group list.')	
				else:
					keyboardButtons = []
					for g_id in get_groups(msg['chat']['id']):
						if is_group_on_db(g_id):
							_callback_data = 'setgroup@' + str(g_id)
							keyboardButtons.append(InlineKeyboardButton(text=groups_db.get_document({'_id':g_id})['group_title'], callback_data= _callback_data))

					markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=[keyboardButtons])
					bot.sendMessage(msg['from']['id'], "Choose a group: ", reply_markup=markup)
			else:
				command_start(bot, msg)
		return

def command_mygroup(bot, msg):
	if is_private(msg):
		if is_user_on_db(msg['chat']['id']):
			choosen_id = users_db.get_document({'_id':msg['chat']['id']})['choosen_group']
			if choosen_id != None:
				group_title = groups_db.get_document({'_id':choosen_id})['group_title']
				bot.sendMessage(msg['chat']['id'], text_msgs['setgroup'].format(group_title=group_title))
			else:
				bot.sendMessage(msg['chat']['id'], text_msgs['info'].format(user_name=msg['chat']['first_name']))
		else:
			command_start(bot, msg)
	return

def command_deleteme(bot, msg):
	if is_private(msg):
		if is_user_on_db(msg['from']['id']):
			users_db.delete_documents({'_id':msg['from']['id']})

			# del users_map.map[msg['from']['id']]
			# save_obj(users_map, "users_map")
			bot.sendMessage(msg['chat']['id'], text='You\'ve been completly removed from the bot\'s database.')
	return

def command_burn(bot, msg):
	if is_group(msg):
		if is_group_on_db(msg['chat']['id']):
			bot.sendMessage(msg['chat']['id'], text='Current chance is set to: ' + str(groups_db.get_document({'_id':msg['chat']['id']})['burn']) + '%')
		else:
			command_start(bot, msg)
	return

def command_setburn(bot, msg, n):
	if is_group(msg):					
		status = bot.getChatMember(msg['chat']['id'], msg['from']['id'])['status']

		if status == 'creator' or status == 'administrator':
			percent = unicode(n)
			
			if '%' in percent:
				percent.replace('%', '')
				percent.strip()

			if percent.isnumeric():
				percent = int(percent)
			else:
				bot.sendMessage(msg['chat']['id'], text='It has to be a numeric value!', reply_to_message_id=msg['message_id'])
				return

			if percent > 100:
				percent = 100
			if percent < 0:
				percent = 0

			bot.sendMessage(msg['chat']['id'], text='Burn probability will be changed to ' + str(percent) + '% in 5 seconds.')
			time.sleep(5)

			groups_db.update_post({'_id':msg['chat']['id']}, 'burn', percent)
			# groups_map[msg['chat']['id']]['burn'] = percent
			# save_obj(groups_map, 'groups_map')
			bot.sendMessage(msg['chat']['id'], text='Burn probability changed to ' + str(percent) + '%.')
		else:
			bot.sendMessage(msg['chat']['id'], text='You\'ve to be an administrator to do that!')

def command_refresh(bot, msg):
	if is_private(msg):
		if is_user_on_db(msg['from']['id']):
			for g_id in get_groups(msg['from']['id']):
				if not is_group_on_db(g_id):
					delete_group(msg['chat']['id'], g_id)
			# save_obj(users_map, "users_map")

			if groups_db.get_document() == None:
				bot.sendMessage(msg['chat']['id'], text='Oops!! Looks like I\'m not in any group right now. Add me to the ones where you wish to use me.')
			else:
				for g in groups_db.find_documents():
					if isMember(bot, msg['chat']['id'], g['_id']) and g['_id'] not in get_groups(msg['chat']['id']):
						users_db.collection.update_one({'_id':msg['chat']['id']}, {'$push':{'groups_list':g['_id']}})
					elif not isMember(bot, msg['chat']['id'], g['_id']) and g['_id'] in get_groups(msg['chat']['id']):
						users_db.collection.update_one({'_id':msg['chat']['id']}, {'$pull':{'groups_list':g['_id']}})

				# save_obj(users_map, "users_map")
				bot.sendMessage(msg['chat']['id'], text='Group list updated.')
				command_setgroup(bot, msg)
		else:
			command_start(bot, msg)
	return


def on_callback_query(bot, msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

	query_data = query_data.split('@', 1)
	if(query_data[0] == 'setgroup' and
		is_user_on_db(from_id) and
		is_group_on_db(int(query_data[1]))):

		users_db.update_post({'_id':from_id}, 'choosen_group', int(query_data[1]))
		# users_map.map[from_id].set_choosen(int(query_data[1]))
		# save_obj(users_map, 'users_map')

		group_title = groups_db.get_document({'_id':int(query_data[1])})['group_title']
		bot.answerCallbackQuery(query_id, text_msgs['setgroup'].format(group_title=group_title))
		
		msg_id = (msg['message']['chat']['id'], msg['message']['message_id'])
		bot.editMessageText(msg_identifier=msg_id, text=text_msgs['setgroup'].format(group_title=group_title), reply_markup=None)

	return

def resend_message_to(bot, message, user, choosen_group_id):
	
	burn = random.randint(1,100) < groups_db.get_document({'_id':choosen_group_id})['burn']

	if burn:
		print 'fowarding message...' 
		bot.forwardMessage(choosen_group_id, message['chat']['id'], message['message_id'])
		return	

	if 'venue' in message:
		print 'sending venue...'
		bot.sendVenue(choosen_group_id, message['venue']['location']['longitude'], message['venue']['location']['latitude'], message['venue']['title'], message['venue']['address'])

	if 'location' in message:
		print 'sending location...'
		bot.sendLocation(choosen_group_id, message['location']['latitude'], message['location']['longitude'])

	if 'contact' in message:
		print 'sending contact...'
		bot.sendContact(choosen_group_id, message['contact']['phone_number'], message['contact']['first_name'])

	if 'voice' in message:
		print 'sending audio...'
		bot.sendVoice(choosen_group_id, message['voice']['file_id'])

	if 'video' in message:
		print 'sending video...'
		bot.sendVideo(choosen_group_id, message['video']['file_id'])

	if 'audio' in message:
		print 'sending audio...'
		bot.sendAudio(choosen_group_id, message['audio']['file_id'])

	if 'photo' in message:
		# print message.photo
		print 'sending photo...'
		bot.sendPhoto(choosen_group_id, message['photo'][-1]['file_id'])

	if 'document' in message:
		print 'sending document...'
		bot.sendDocument(choosen_group_id, message['document']['file_id'])

	if 'sticker' in message:
		print 'sending sticker...'
		bot.sendSticker(choosen_group_id, message['sticker']['file_id'])

	if 'text' in message:
		print 'sending message...'
		bot.sendMessage(choosen_group_id, message['text'])

# Excepction

class SimpleMessageException(Exception):
	pass
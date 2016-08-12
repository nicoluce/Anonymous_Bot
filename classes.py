# Anonymous_Bot - Classes
# Nicolas Luce

class User(object):
	def __init__(self, msg):
		self.first_name = msg['from']['first_name']
		if 'last_name' in msg['from']:
			self.last_name = msg['from']['last_name']
		else:
			self.last_name = ''

		if 'username' in msg['from']:
			self.username = msg['from']['username']
		else:
			self.username = ''

		self.id = msg['from']['id']
	def name(self):
		return self.first_name + ' ' + self.last_name 


class GroupChat():
	"""docstring for ChatGroup"""
	def __init__(self, msg):
		self.id = msg['chat']['id']
		self.title = msg['chat']['title']

class Users_Map():
	"""docstring for Users_Map"""
	def __init__(self):
		self.map = {}

	def get_choosen(self, user_id):
		return self.map[user_id].choosen

	def get_groups(self, user_id):
		return self.map[user_id].group_list

	def add_user(self, user):
		self.map[user.id] = Anon_User(user)

class Anon_User():
	"""docstring for Anon_User"""
	def __init__(self, user):
		self.user = user
		self.group_list = []
		self.choosen = None

	def add_group(self, group_id):
		if group_id not in self.group_list:
			self.group_list.append(group_id)

	def set_choosen(self, group_id):
		self.choosen = group_id
		return

	def delete_group(self, group_id):
		for i in xrange(0,len(self.group_list)):
			if self.group_list[i] == group_id:
				del self.group_list[i]
				return


global users_map
# users_map = Users_Map()
global groups_map
# groups_map = {}
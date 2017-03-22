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


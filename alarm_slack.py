from slacker import Slacker

class SlackAPI:
	def there_is_channel(self):
		channel_body = self.slack.conversations.list().body['channels']
		for channels_name in channel_body:
			if channels_name['name'] == self.name:
				return True
		return False


	def __init__(self):
		#AIR 토큰
		self.token = "xoxb-2367000478-1333178603376-rGvgCU5HjCpvXNWlNtnTR0uf"
		self.slack = Slacker(self.token)
		self.name = "crawl_alarm"
	#채널 이름 변경


	def channel_name_set(self,chan_name):
		self.name = chan_name


	def make_channel(self):
		if not self.there_is_channel():
			self.slack.conversations.create(self.name)

	def send_msg(self,msg):
		self.slack.chat.post_message('#'+self.name,msg)

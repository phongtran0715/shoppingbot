class AccountModel():
	def __init__(self, account_type=None, name=None, user_name=None, password=None, proxy=None, profile=None):
		self.type, self.name, self.user_name, self.password, self.proxy, self.profile = account_type, name, user_name, password, proxy, profile

	def get_account_type(self):
		return self.account_type

	def set_account_type(self, account_type):
		self.account_type = account_type

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name

	def get_user_name(self):
		return self.user_name

	def set_user_name(self, user_name):
		self.user_name = user_name

	def get_password(self):
		return self.password

	def set_password(self, password):
		self.password = password

	def get_proxy(self):
		return self.proxy

	def set_proxy(self, proxy):
		self.proxy = proxy

	def get_profile(self):
		return self.profile

	def set_profile(self, profile):
		self.profile = profile


class AccountModel():
	def __init__(self, account_id=None, account_name = None, site = None, user_name = None, password = None, proxy = None, billing_profile = None):
		self.account_id = account_id
		self.account_name = account_name
		self.site = site
		self.user_name = user_name
		self.password = password
		self.proxy = proxy
		self.billing_profile = billing_profile

	def get_account_id(self):
		return self.account_id

	def set_account_id(self, account_id):
		self.account_id = account_id

	def get_site(self):
		return self.site

	def set_site(self, site):
		self.site = site

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

	def get_billing_profile(self):
		return self.billing_profile

	def set_billing_profile(self, billing_profile):
		self.billing_profile = billing_profile
class TaskModel:
	def __init__(self, task_id=None, product=None, site=None, monitor_proxy=None,
		monitor_delay=None, error_delay=None, max_price=None, max_quantity=None,
		account=None):
		self.task_id = task_id
		self.product = product
		self.site = site
		self.monitor_proxy = monitor_proxy
		self.monitor_delay = monitor_delay
		self.error_delay = error_delay
		self.max_price = max_price
		self.max_quantity = max_quantity
		self.account = account

	def get_task_id(self):
		return self.task_id

	def set_task_id(self, task_id):
		self.task_id = task_id

	def get_product(self):
		return self.product

	def set_item(self, product):
		self.product = product

	def get_site(self):
		return self.site

	def set_site(self, site):
		self.site = site

	def get_monitor_proxy(self):
		return self.monitor_proxy

	def set_monitor_proxy(self, monitor_proxy):
		self.monitor_proxy = monitor_proxy

	def get_monitor_delay(self):
		return self.monitor_delay

	def set_monitor_delay(self, monitor_delay):
		self.monitor_delay = monitor_delay

	def get_error_delay(self):
		return self.error_delay

	def set_error_delay(self, error_delay):
		self.error_delay = error_delay

	def get_max_price(self):
		return self.max_price

	def set_max_price(self):
		self.max_price = max_price

	def get_max_quantity(self):
		return self.max_quantity

	def set_max_quantity(self, max_quantity):
		self.max_quantity = max_quantity

	def get_account(self):
		return self.account

	def set_account(self, account):
		self.account = account

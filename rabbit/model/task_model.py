class TaskModel:
	def __init__(self, task_id=None, item=None, category=None, size=None,
		colour=None, billing_profile=None, task_type=None, proxy=None,
		status=None, details=None):
		self.task_id = task_id
		self.item = item
		self.category = category
		self.size = size
		self.colour = colour
		self.billing_profile = billing_profile
		self.task_type = task_type
		self.proxy = proxy
		self.status = status
		self.details = details

	def get_task_id(self):
		return self.task_id

	def set_task_id(self, task_id):
		self.task_id = task_id

	def get_item(self):
		return self.item

	def set_item(self, item):
		self.item = item

	def get_category(self):
		return self.category

	def set_category(self, category):
		self.category = category

	def get_size(self):
		return self.size

	def set_size(self, size):
		self.size = size

	def get_colour(self):
		return self.colour

	def set_colour(self, colour):
		self.colour = colour

	def get_billing_profile(self):
		return self.billing_profile

	def set_billing_profile(self, billing_profile):
		self.billing_profile = billing_profile

	def get_task_type(self):
		return self.task_type

	def set_task_type(self):
		self.task_type = task_type

	def get_proxy(self):
		return self.proxy

	def set_proxy(self, proxy):
		self.proxy = proxy

	def get_status(self):
		return self.status

	def set_status(self, status):
		self.status = status

	def get_details(self):
		return self.detais

	def set_details(self, details):
		self.details = details

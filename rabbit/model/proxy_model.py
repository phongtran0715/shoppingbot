class ProxyModel():
	def __init__(self, proxy_id=None, name=None, content=None):
		self.proxy_id, self.name, self.content = proxy_id, name, content

	def get_proxy_id(self):
		return self.proxy_id

	def set_proxy_id(self, proxy_id):
		self.proxy_id = proxy_id

	def get_name(self):
		return self.name
	
	def set_name(self, name):
		self.name = name

	def get_content(self):
		return self.content

	def set_content(self, content):
		self.content = content
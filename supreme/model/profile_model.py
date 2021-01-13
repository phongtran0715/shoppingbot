class ProfileModel():
	def __init__(self, profile_id=None, name=None, card_name=None, email=None, phone=None,
		address=None, address2=None, postcode=None, city=None, state=None, country==None,
		card_number=None,exp_month=None, exp_year=None, cvv=None, card_type=None):
		self.profile_id = profile_id
		self.name = name
		self.card_name = card_name
		self.email = email
		self.phone = phone
		self.address = address
		self.address2 = address2
		self.postcode = postcode
		self.city = city
		self.state = state
		self.country = country
		self.card_number = card_number
		self.exp_month = exp_month
		self.exp_year = exp_year
		self.cvv = cvv
		self.card_type = card_type

	def get_profile_id(self):
		return self.profile_id

	def set_profile_id(self, profile_id):
		self.profile_id = profile_id

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name

	def get_card_name(self):
		return self.card_name

	def set_card_name(self, card_name):
		self.card_name = card_name

	def get_email(self):
		return self.email

	def set_email(self, email):
		self.email = self.email

	def get_phone(self):
		return self.phone

	def set_phone(self, phone):
		return self.phone

	def get_address(self):
		return self.address

	def set_address(self, address):
		self.address = address

	def get_address2(self):
		return self.address2

	def set_address2(self, address2):
		self.address2 = address2

	def get_postcode(self):
		return self.postcode

	def set_postcode(self, postcode):
		self.postcode = postcode

	def get_city(self):
		return self.city

	def set_city(self, city):
		self.city = city

	def get_state(self):
		return self.state

	def set_state(self, state):
		self.state = state

	def get_country(self):
		return self.country

	def set_country(self, country):
		self.country = country

	def get_card_number(self):
		return self.card_number

	def set_city(self, card_number):
		self.card_number = card_number

	def get_exp_month(self):
		return self.exp_month

	def set_exp_month(self, exp_month):
		self.exp_month = exp_month

	def get_exp_year(self):
		return self.exp_year

	def set_exp_year(self, exp_year):
		self.exp_year = exp_year

	def get_cvv(self):
		return self.cvv

	def set_cvv(self, cvv):
		self.cvv = cvv

	def get_card_type(self):
		return self.card_type

	def set_card_type(self, card_type):
		self.card_type = card_type


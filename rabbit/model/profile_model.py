class ProfileModel():
	def __init__(self, profile_id=None, profile_name=None, shipping_first_name=None, shipping_last_name=None, shipping_email=None,
		shipping_phone=None, shipping_address_1=None, shipping_address_2=None, shipping_city=None, shipping_zipcode=None,
		shipping_state=None, shipping_country=None,
		billing_first_name=None, billing_last_name=None, billing_email=None, billing_phone=None, billing_address_1=None, billing_address_2=None,
		billing_city=None, billing_zipcode=None, billing_state=None, billing_country=None, 
		card_type=None, card_number=None, card_name=None, card_cvv=None, exp_month=None, exp_year=None):
		self.profile_id = profile_id
		self.profile_name = profile_name
		
		self.shipping_first_name = shipping_first_name
		self.shipping_last_name = shipping_last_name
		self.shipping_email = shipping_email
		self.shipping_phone = shipping_phone
		self.shipping_address_1 = shipping_address_1
		self.shipping_address_2 = shipping_address_2
		self.shipping_city = shipping_city
		self.shipping_zipcode = shipping_zipcode
		self.shipping_state = shipping_state
		self.shipping_country = shipping_country
		
		self.billing_first_name = billing_first_name
		self.billing_last_name = billing_last_name
		self.billing_email = billing_email
		self.billing_phone = billing_phone
		self.billing_address_1 = billing_address_1
		self.billing_address_2 = billing_address_2
		self.billing_city = billing_city
		self.billing_zipcode = billing_zipcode
		self.billing_state = billing_state
		self.billing_country = billing_country
		
		self.card_type = card_type
		self.card_number = card_number
		self.card_name = card_name
		self.card_cvv = card_cvv
		self.exp_month = exp_month
		self.exp_year = exp_year

	def get_profile_id(self):
		return self.profile_id

	def set_profile_id(self, profile_id):
		self.profile_id = profile_id

	def get_profile_name(self):
		return self.profile_name

	def set_profile_name(self, profile_name):
		self.profile_name = profile_name

	def get_shipping_first_name(self):
		return self.shipping_first_name

	def set_shipping_first_name(self, shipping_first_name):
		self.shipping_first_name = shipping_first_name

	def get_shipping_last_name(self):
		return self.shipping_last_name

	def set_shipping_last_name(self, shipping_last_name):
		self.shipping_last_name = self.shipping_last_name

	def get_shipping_email(self):
		return self.shipping_email

	def set_shipping_email(self, shipping_email):
		self.shipping_email = shipping_email

	def get_shipping_phone(self):
		return self.shipping_phone

	def set_shipping_phone(self, shipping_phone):
		self.shipping_phone = shipping_phone

	def get_shipping_address_1(self):
		return self.shipping_address_1

	def set_shipping_address_1(self, shipping_address_1):
		self.shipping_address_1 = shipping_address_1

	def get_shipping_address_2(self):
		return self.shipping_address_2

	def set_shipping_address_2(self, shipping_address_2):
		self.shipping_address_2 = shipping_address_2

	def get_shipping_city(self):
		return self.shipping_city

	def set_shipping_city(self, shipping_city):
		self.shipping_city = shipping_city

	def get_shipping_state(self):
		return self.shipping_state

	def set_shipping_state(self, shipping_state):
		self.shipping_state = shipping_state

	def get_shipping_zipcode(self):
		return self.shipping_zipcode

	def set_shipping_zipcode(self, shipping_zipcode):
		self.shipping_zipcode = shipping_zipcode

	def get_shipping_state(self):
		return self.shipping_state

	def set_shipping_state(self, shipping_state):
		self.shipping_state = shipping_state

	def get_shipping_country(self):
		return self.shipping_country

	def set_shipping_country(self, shipping_country):
		self.shipping_country = shipping_country

	def get_billing_first_name(self):
		return self.billing_first_name

	def set_billing_first_name(self, billing_first_name):
		self.billing_first_name = billing_first_name

	def get_billing_last_name(self):
		return self.billing_last_name

	def set_billing_last_name(self, billing_last_name):
		self.billing_last_name = self.billing_last_name

	def get_billing_email(self):
		return self.billing_email

	def set_billing_email(self, billing_email):
		self.billing_email = billing_email

	def get_billing_phone(self):
		return self.billing_phone

	def set_billing_phone(self, billing_phone):
		self.billing_phone = billing_phone

	def get_billing_address_1(self):
		return self.billing_address_1

	def set_billing_address_1(self, billing_address_1):
		self.billing_address_1 = billing_address_1

	def get_billing_address_2(self):
		return self.billing_address_2

	def set_billing_address_2(self, billing_address_2):
		self.billing_address_2 = billing_address_2

	def get_billing_city(self):
		return self.billing_city

	def set_billing_city(self, billing_city):
		self.billing_city = billing_city

	def get_billing_state(self):
		return self.billing_state

	def set_billing_state(self, billing_state):
		self.billing_state = billing_state

	def get_billing_zipcode(self):
		return self.billing_zipcode

	def set_billing_zipcode(self, billing_zipcode):
		self.billing_zipcode = billing_zipcode

	def get_billing_state(self):
		return self.billing_state

	def set_billing_state(self, billing_state):
		self.billing_state = billing_state

	def get_billing_country(self):
		return self.billing_country

	def set_billing_country(self, billing_country):
		self.billing_country = billing_country

	def get_card_type(self):
		return self.card_type

	def set_card_type(self, card_type):
		self.card_type = card_type

	def get_card_number(self):
		return self.card_number

	def set_card_number(self, card_number):
		self.card_number = card_number

	def get_card_name(self):
		return self.card_name

	def set_card_name(self, card_name):
		self.card_name = card_name

	def get_card_cvv(self):
		return self.card_cvv

	def set_card_cvv(self, card_cvv):
		self.card_cvv = card_cvv

	def get_exp_month(self):
		return self.exp_month

	def set_exp_month(self, exp_month):
		self.exp_month = exp_month

	def get_exp_year(self):
		return self.exp_year

	def set_exp_year(self, exp_year):
		self.exp_year = exp_year
import os, sys, requests
import time
from view.keyword.look_for_stock import find_item_ids
from view.keyword.atc_checkout import add_to_cart, checkout


class KeywordsProcessing:
	"""docstring for KeywordsProcessing"""
	def __init__(self, item, category, colour, size, profile, proxy):
		super(KeywordsProcessing, self).__init__()
		self.item = item
		self.category = category
		self.colour = colour
		self.size = size
		self.profile = profile
		self.proxy = proxy

	def process_keyword(self):
		print("process keyword : " + str(self.item))
		delay = 3
		start_checkout_time = time.time()
		item_id, size_id, style_id = find_item_ids(self.item, self.category, self.size, self.colour, self.proxy)
		if item_id is None:
			msg = 'Can not find product!'
			print(msg)
			return False, msg

		print('Found product: id = {} - size : {} - style : {}'.format(item_id, size_id, style_id))
		session = add_to_cart(item_id, size_id, style_id)
		if session is None:
			msg = 'Add to card false!'
			print(msg)
			return False, msg
		
		if checkout(session, self.profile, delay, self.proxy, start_checkout_time):
			msg = 'Success'
			print(msg)
			return True, msg
		else:
			msg = 'Checkout false'
			print(msg)
			return False, msg


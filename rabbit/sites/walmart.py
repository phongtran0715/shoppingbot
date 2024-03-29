from sites.walmart_encryption import walmart_encryption as w_e
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from PyQt5 import QtCore
import urllib, requests, time, lxml.html, json, sys, os
import logging
from model.task_model import TaskModel
from PyQt5.QtSql import QSqlDatabase
from utils.rabbit_util import RabbitUtil
from utils.twocaptcha_utils import solve_captcha
from configparser import ConfigParser
import pickle, random


logger = logging.getLogger(__name__)

monitor_user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
]

shopping_user_agent_list = [
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
]

class Walmart:
	def __init__(self, status_signal, image_signal, wait_poll_signal, polling_wait_condition, task_model):

		self.status_signal = status_signal
		self.image_signal = image_signal
		self.product = task_model.get_product()
		self.task_id = task_model.get_task_id()
		self.monitor_delay = float(task_model.get_monitor_delay())
		self.error_delay = float(task_model.get_error_delay())
		self.monitor_proxies = task_model.get_monitor_proxy()
		self.account = task_model.get_account()
		self.max_quantity = task_model.get_max_quantity()
		self.max_price = task_model.get_max_price()
		####### Browser/Captcha Polling Variables ######
		self.captcha_mutex = QtCore.QMutex()
		self.captcha_wait_condition = polling_wait_condition
		self.wait_poll_signal = wait_poll_signal
		#################################################
		# create database connection
		self.db_conn = QSqlDatabase.addDatabase("QSQLITE", "walmart_db_conn_" + str(task_model.get_task_id()))
		self.db_conn.setDatabaseName(os.path.join('data', 'rabbit_db.sqlite'))
		if not self.db_conn.open():
			logger.error("Walmart | Task id {} - Open conection false!".format(self.task_id))
			return

		# create config parse
		self.config = ConfigParser()
		self.config.read(os.path.join('data', 'config.ini'))

		self.dont_buy = True
		if self.config.getint('general', 'dev_mode') == 0:
			self.dont_buy = False

		self.session = requests.Session()

		if self.max_quantity is None or int(self.max_quantity) == 0:
			self.max_quantity = 1

		starting_msg = "Starting"
		self.status_signal.emit({"message": starting_msg, "status": "normal", "task_id" : self.task_id})
		self.product_image, offer_id = self.monitor()
		if offer_id is None:
			return
		for account_name in self.account.split(','):
			account_item = RabbitUtil.get_account(account_name, self.db_conn)
			if account_item is None:
				continue
			logger.info("Walmart | Task id {} - Processing for account : {}".format(self.task_id, account_name))
			self.user_agent = random.choice(shopping_user_agent_list)
			did_add = self.atc(offer_id, account_item)
			count_add = 1
			while did_add is False and count_add <= 3:
				did_add = self.atc(offer_id, account_item)
				count_add += 1
			if did_add is False:
				return

			item_id, fulfillment_option, ship_method = self.check_cart_items(account_item)
			self.submit_shipping_method(item_id, fulfillment_option, ship_method, account_item)
			self.submit_shipping_address(account_item)
			card_data, PIE_key_id, PIE_phase = self.get_PIE(account_item)
			pi_hash = self.submit_payment(card_data, PIE_key_id, PIE_phase, account_item)
			self.submit_billing(pi_hash, account_item)
			self.submit_order(account_item)

	def monitor(self):
		headers = {
			"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"cache-control": "max-age=0",
			"upgrade-insecure-requests": "1",
			"user-agent": random.choice(monitor_user_agent_list)
		}
		image_found = False
		product_image = ""
		while True:
			self.status_signal.emit({"message": "Monitoring Product Page", "status": "normal", "task_id" : self.task_id})
			try:
				monitor_proxy = RabbitUtil.get_proxy(self.monitor_proxies, self.db_conn)
				monitor_session = requests.Session()
				if monitor_proxy is not None and monitor_proxy != "":
					monitor_session.proxies.update(monitor_proxy)
					logger.info("Walmart | Task id {} - Monitoring by proxy : {}".format(self.task_id, monitor_proxy))

				r = monitor_session.get(self.product, headers=headers)
				if r.status_code == 200:
					# check for captcha page
					if self.is_captcha(r.text):
						self.status_signal.emit({"message": "CAPTCHA - Opening Product Page", "status": "error", "task_id" : self.task_id})
						# No need to handle captcha - we have multiple proxy
						# self.handle_captcha(self.product)
						continue

					doc = lxml.html.fromstring(r.text)
					vendor = doc.xpath('//a[@class="seller-name"]/text()')[0]
					if "walmart" != vendor.lower():
						self.status_signal.emit({"message": "Seller is not Walmart", "status": "error", "task_id" : self.task_id})
						return "", None
					if not image_found:
						product_image = doc.xpath('//meta[@property="og:image"]/@content')[0]
						self.image_signal.emit(product_image)
						image_found = True
					price = float(doc.xpath('//span[@itemprop="price"]/@content')[0])
					if "add to cart" in r.text.lower():
						if self.max_price != "" and int(self.max_price) > 0:
							if float(self.max_price) < price:
								self.status_signal.emit({"message": "Waiting For Price Restock", "status": "normal", "task_id" : self.task_id})
								monitor_session.cookies.clear()
								time.sleep(self.monitor_delay)
								continue
						offer_id = json.loads(doc.xpath('//script[@id="item"]/text()')[0])["item"]["product"]["buyBox"][
							"products"][0]["offerId"]
						logger.info("Found product")
						return product_image, offer_id
					self.status_signal.emit({"message": "Waiting For Restock", "status": "normal", "task_id" : self.task_id})
					monitor_session.cookies.clear()
					time.sleep(self.monitor_delay)
				else:
					logger.error("Status code {}".format(r.status_code))
					self.status_signal.emit({"message": "Error Loading Product Page", "status": "error", "task_id" : self.task_id})
					time.sleep(self.monitor_delay)
			except Exception as e:
				self.status_signal.emit({"message": "Error Loading Product Page (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)

	def atc(self, offer_id, account):
		headers = {
			"accept": "application/json",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": self.product,
			"user-agent": self.user_agent,
			"wm_offer_id": offer_id
		}
		profile = RabbitUtil.get_profile(account.get_profile(), self.db_conn)
		body = {"offerId": offer_id, "quantity": int(self.max_quantity),
				"location": {"postalCode": profile.get_shipping_zipcode(), "city": profile.get_shipping_city(),
							 "state": profile.get_shipping_state(), "isZipLocated": True},
				"shipMethodDefaultRule": "SHIP_RULE_1"}

		while True:
			self.status_signal.emit({"message": "Adding To Cart", "status": "normal", "task_id" : self.task_id})
			try:
				shopping_proxy = RabbitUtil.get_proxy(account.get_proxy(), self.db_conn)
				if shopping_proxy is not None and shopping_proxy != "":
					logger.info("Walmart | Task id : {} - Shopping proxy : : {}".format(self.task_id, shopping_proxy))
					self.session.proxies.update(shopping_proxy)
				else:
					logger.info("Walmart | Task id : {} - Shopping without proxy".format(self.task_id))

				# set cookies for session
				if os.path.isfile('walmart_cookies.pkl'):
					cookies = pickle.load(open("walmart_cookies.pkl", "rb"))
					for c in cookies:
						if c['name'] not in [x.name for x in self.session.cookies]:
							self.session.cookies.set(c['name'], c['value'], path=c['path'], domain=c['domain'])
				
				r = self.session.post("https://www.walmart.com/api/v3/cart/guest/:CID/items", json=body,
									  headers=headers)

				# check for captcha page
				if self.is_captcha(r.text):
					self.status_signal.emit({"message": "Opening CAPTCHA", "status": "error", "task_id" : self.task_id})
					self.handle_captcha(self.product)
					return False

				if r.status_code == 201 or r.status_code == 200 and json.loads(r.text)["checkoutable"] == True:
					self.status_signal.emit({"message": "Added To Cart", "status": "carted","task_id" : self.task_id})
					return True
				else:
					logger.info("Walmart | Task id : {} - status code : {}".format(self.task_id, r.status_code))
					logger.error(r.text)
					if 'redirectUrl' in r.text:
						blocked_url = "https://www.walmart.com" + json.loads(r.text)["redirectUrl"]
						self.handle_captcha(blocked_url)
						self.status_signal.emit({"message": "Error Adding To Cart", "status": "error","task_id" : self.task_id})
						time.sleep(self.error_delay)
					else:
						self.status_signal.emit({"message": "Error Adding To Cart", "status": "error","task_id" : self.task_id})
			except Exception as e:
				self.status_signal.emit({"message": "Error Adding To Cart (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)

	def check_cart_items(self, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": self.user_agent,
			"wm_vertical_id": "0",
			"wm_cvv_in_session": "true",
		}

		profile = RabbitUtil.get_profile(account.get_profile(), self.db_conn)
		body = {"postalCode": profile.get_shipping_zipcode(), "city": profile.get_shipping_city(),
				"state": profile.get_shipping_state(), "isZipLocated": True, "crt:CRT": "", "customerId:CID": "",
				"customerType:type": "", "affiliateInfo:com.wm.reflector": "", "storeList": []}

		while True:
			self.status_signal.emit({"message": "Loading Cart Items", "status": "normal", "task_id" : self.task_id})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout/v3/contract?page=CHECKOUT_VIEW", json=body,
									  headers=headers)# this sometimes returns json data related to loading a captcha.js file so that could be intercepted when requests fail

				if r.status_code == 201 or r.status_code == 200:
					r = json.loads(r.text)["items"][0]
					item_id = r["id"]
					fulfillment_option = r["fulfillmentSelection"]["fulfillmentOption"]
					ship_method = r["fulfillmentSelection"]["shipMethod"]
					self.status_signal.emit({"message": "Loaded Cart Items", "status": "normal", "task_id" : self.task_id})
					return item_id, fulfillment_option, ship_method
				else:
					if json.loads(r.text)["message"] == "Item is no longer in stock.":
						self.status_signal.emit({"message": "Waiting For Restock", "status": "normal", "task_id" : self.task_id})
						time.sleep(self.monitor_delay)
					else:
						if self.is_captcha(r.text):
							self.handle_captcha("https://www.walmart.com/checkout")
						self.status_signal.emit(
							{"message": "Error Loading Cart Items, Got Response: " + str(r.text), "status": "error", "task_id" : self.task_id})
						time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"message": "Error Loading Cart Items (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)

	def submit_shipping_method(self, item_id, fulfillment_option, ship_method, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": self.user_agent,
			"wm_vertical_id": "0"
		}
		body = {"groups": [{"fulfillmentOption": fulfillment_option, "itemIds": [item_id], "shipMethod": ship_method}]}
		while True:
			self.status_signal.emit({"message": "Submitting Shipping Method", "status": "normal", "task_id" : self.task_id})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/fulfillment", json=body,
									  headers=headers)
				if r.status_code == 200:
					try:
						r = json.loads(r.text)
						self.status_signal.emit({"message": "Submitted Shipping Method", "status": "normal","task_id" : self.task_id})
						return
					except:
						pass
				self.status_signal.emit({"message": "Error Submitting Shipping Method", "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"message": "Error Submitting Shipping Method (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)

	def submit_shipping_address(self, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"content-type": "application/json",
			"inkiru_precedence": "false",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": self.user_agent,
			"wm_vertical_id": "0"
		}
		profile = RabbitUtil.get_profile(account.get_profile(), self.db_conn)
		body = {
			"addressLineOne": profile.get_shipping_address_1(),
			"city": profile.get_shipping_city(),
			"firstName": profile.get_shipping_first_name(),
			"lastName": profile.get_shipping_last_name(),
			"phone": profile.get_shipping_phone(),
			"email": profile.get_shipping_email(),
			"marketingEmailPref": False,
			"postalCode": profile.get_shipping_zipcode(),
			"state": profile.get_shipping_state(),
			"countryCode": "USA",
			"addressType": "RESIDENTIAL",
			"changedFields": []
		}
		if profile.get_shipping_address_2() != "":
			body.update({"addressLineTwo": profile.get_shipping_address_2()})
		while True:
			self.status_signal.emit({"message": "Submitting Shipping Address", "status": "normal","task_id" : self.task_id})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/shipping-address",
									  json=body, headers=headers)
				if r.status_code == 200:
					try:
						r = json.loads(r.text)
						self.status_signal.emit({"message": "Submitted Shipping Address", "status": "normal", "task_id" : self.task_id})
						return
					except:
						pass
				self.status_signal.emit({"message": "Error Submitting Shipping Address", "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"message": "Error Submitting Shipping Address (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error","task_id" : self.task_id})
				time.sleep(self.error_delay)

	def get_PIE(self, account):
		headers = {
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"Connection": "keep-alive",
			"Host": "securedataweb.walmart.com",
			"Referer": "https://www.walmart.com/",
			"User-Agent": self.user_agent
		}
		profile = RabbitUtil.get_profile(account.get_profile(), self.db_conn)
		while True:
			self.status_signal.emit({"message": "Getting Checkout Data", "status": "normal", "task_id" : self.task_id})
			try:
				r = self.session.get(
					"https://securedataweb.walmart.com/pie/v1/wmcom_us_vtg_pie/getkey.js?bust=" + str(int(time.time())),
					headers=headers)
				if r.status_code == 200:
					PIE_L = int(r.text.split("PIE.L = ")[1].split(";")[0])
					PIE_E = int(r.text.split("PIE.E = ")[1].split(";")[0])
					PIE_K = str(r.text.split('PIE.K = "')[1].split('";')[0])
					PIE_key_id = str(r.text.split('PIE.key_id = "')[1].split('";')[0])
					PIE_phase = int(r.text.split('PIE.phase = ')[1].split(';')[0])
					card_data = w_e.encrypt(profile.get_card_number(), profile.get_card_cvv(), PIE_L, PIE_E, PIE_K,
											PIE_key_id, PIE_phase)
					self.status_signal.emit({"message": "Got Checkout Data", "status": "normal", "task_id" : self.task_id})
					return card_data, PIE_key_id, PIE_phase
				self.status_signal.emit({"message": "Error Getting Checkout Data", "status": "error","task_id" : self.task_id})
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"message": "Error Getting Checkout Data (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error","task_id" : self.task_id})
				time.sleep(self.error_delay)

	def submit_payment(self, card_data, PIE_key_id, PIE_phase, account):
		headers = {
			"accept": "application/json",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": self.user_agent
		}
		# "inkiru_precedence": "false",
		profile = RabbitUtil.get_profile(account.get_profile(), self.db_conn)
		body = {
			"encryptedPan": card_data[0],
			"encryptedCvv": card_data[1],
			"integrityCheck": card_data[2],
			"keyId": PIE_key_id,
			"phase": PIE_phase,
			"state": profile.get_billing_state(),
			"postalCode": profile.get_billing_zipcode(),
			"addressLineOne": profile.get_billing_address_1(),
			"addressLineTwo": profile.get_billing_address_2(),
			"city": profile.get_billing_city(),
			"firstName": profile.get_billing_first_name(),
			"lastName": profile.get_billing_last_name(),
			"expiryMonth": profile.get_exp_month(),
			"expiryYear": profile.get_exp_year(),
			"phone": profile.get_billing_phone(),
			"cardType": profile.get_card_type().upper(),
			"isGuest": True
		}
		while True:
			self.status_signal.emit({"message": "Submitting Payment", "status": "normal", "task_id" : self.task_id})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout-customer/:CID/credit-card", json=body,
									  headers=headers)
				if r.status_code == 200:
					pi_hash = json.loads(r.text)["piHash"]
					self.status_signal.emit({"message": "Submitted Payment", "status": "normal", "task_id" : self.task_id})
					return pi_hash
				self.status_signal.emit({"message": "Error Submitting Payment", "status": "error","task_id" : self.task_id})
				logger.error("Walmart | Task id : {} - Error Submitting Payment - Status code : {} - msg : {}".format(self.task_id, r.status_code, r.text))
				if self.check_browser(account):
					return
				time.sleep(self.error_delay)
				count += 1
			except Exception as e:
				self.status_signal.emit({"message": "Error Submitting Payment (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)

	def submit_billing(self, pi_hash, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": self.user_agent,
			"wm_vertical_id": "0"
		}

		profile = RabbitUtil.get_profile(account.get_profile(), self.db_conn)
		card_data, PIE_key_id, PIE_phase = self.get_PIE(account)
		body = {
			"payments": [{
				"paymentType": "CREDITCARD",
				"cardType": profile.get_card_type().upper(),
				"firstName": profile.get_billing_first_name(),
				"lastName": profile.get_billing_last_name(),
				"addressLineOne": profile.get_billing_address_1(),
				"addressLineTwo": profile.get_billing_address_2(),
				"city": profile.get_billing_city(),
				"state": profile.get_billing_state(),
				"postalCode": profile.get_billing_zipcode(),
				"expiryMonth": profile.get_exp_month(),
				"expiryYear": profile.get_exp_year(),
				"email": profile.get_billing_email(),
				"phone": profile.get_billing_phone(),
				"encryptedPan": card_data[0],
				"encryptedCvv": card_data[1],
				"integrityCheck": card_data[2],
				"keyId": PIE_key_id,
				"phase": PIE_phase,
				"piHash": pi_hash
			}]
		}
		while True:
			self.status_signal.emit({"message": "Submitting Billing", "status": "normal", "task_id" : self.task_id})
			try:
				r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/payment", json=body,
									  headers=headers)
				if r.status_code == 200:
					try:
						r = json.loads(r.text)
						self.status_signal.emit({"message": "Submitted Billing", "status": "normal","task_id" : self.task_id})
						return
					except:
						pass
				self.status_signal.emit({"message": "Error Submitting Billing", "status": "error","task_id" : self.task_id})
				# if self.check_browser(account):
				# 	return
				time.sleep(self.error_delay)
			except Exception as e:
				self.status_signal.emit({"message": "Error Submitting Billing (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)

	def submit_order(self, account):
		headers = {
			"accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en-US,en;q=0.9",
			"content-type": "application/json",
			"origin": "https://www.walmart.com",
			"referer": "https://www.walmart.com/checkout/",
			"user-agent": self.user_agent,
			"wm_vertical_id": "0"
		}
		profile = RabbitUtil.get_profile(account.get_profile(), self.db_conn)
		if self.dont_buy is True:
			# TODO: this used to open the page up with everything filled out but only works for some users
			self.status_signal.emit({"message":"Mock Opening Checkout Page","status":"success", "task_id" : self.task_id})
			RabbitUtil.send_webhook("OP", "Walmart", account.get_account_name(), self.task_id, self.product_image)
			return             

		while True:
			self.status_signal.emit({"message": "Submitting Order", "status": "alt", "task_id" : self.task_id})
			try:
				r = self.session.put("https://www.walmart.com/api/checkout/v3/contract/:PCID/order", json={},
									 headers=headers)
				try:
					logger.info(r.text)
					json.loads(r.text)["order"]
					self.status_signal.emit({"message": "Order Placed", "status": "success", "task_id" : self.task_id})
					RabbitUtil.send_webhook("OP", "Walmart", account.get_account_name(), self.task_id, self.product_image)
					return
				except:
					self.status_signal.emit({"message": "Payment Failed", "status": "error", "task_id" : self.task_id})

					# open the page for checkout if failed to auto submit
					# self.handle_captcha("https://www.walmart.com/checkout/#/payment")
					# if self.check_browser(account):
					# 	return

					RabbitUtil.send_webhook("PF", "Walmart", account.get_account_name(), self.task_id, self.product_image)
					# delay for next time
					time.sleep(self.SHORT_TIMEOUT)
					return
			except Exception as e:
				self.status_signal.emit({"message": "Error Submitting Order (line {} {} {})".format(
					sys.exc_info()[-1].tb_lineno, type(e).__name__, e), "status": "error", "task_id" : self.task_id})
				time.sleep(self.error_delay)

	def check_browser(self, account):
		profile = RabbitUtil.get_profile(account.get_profile(), self.db_conn)
		if True:
			self.status_signal.emit(
				{"message": "Browser Ready", "status": "alt", "url": "https://www.walmart.com/checkout/#/payment",
				 "cookies": [{"name": cookie.name, "value": cookie.value, "domain": cookie.domain} for cookie in
							 self.session.cookies], "task_id" : self.task_id})
			RabbitUtil.send_webhook("B", "Walmart", account.get_account_name(), self.task_id, self.product_image)
			return True
		return False

	def handle_captcha(self, url_to_open, close_window_after=True,redirect=False):
		'''added redirect arg since captchas are lost when redirecting to the page that triggered them
		this opens up chrome browser to get prompted with captcha'''
		# options = webdriver.ChromeOptions()
		# options.add_argument('--ignore-certificate-errors') #removes SSL errors from terminal
		# options.add_experimental_option("excludeSwitches", ["enable-logging"]) #removes device adapter errors from terminal
		# browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
		logger.info("Walmart | Task id : {} - handle captcha; url: {}".format(self.task_id, url_to_open))
		browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
		browser.get(url_to_open)

		# pass current session cookies to browser before loading url
		for c in self.session.cookies:
				browser.add_cookie({
					'name': c.name,
					'value': c.value,
					'domain': c.domain,
					'path': c.path
				})

		time.sleep(3)
		if "blocked" in str(browser.current_url):            	
			# solve captcha by api
			logger.info("Walmart | Task id : {} - Waiting 2captcha to solve recaptcha...".format(self.task_id))
			sitekey = browser.find_element_by_xpath('//*[@id="px-captcha"]/div').get_attribute("data-sitekey")
			captcha_result  = solve_captcha(str(browser.current_url), str(sitekey))

			browser.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0]', captcha_result['code'])
			browser.execute_script("handleCaptcha('{}');".format(captcha_result['code']))

		for c in browser.get_cookies():
			if c['name'] not in [x.name for x in self.session.cookies]:
				self.session.cookies.set(c['name'], c['value'], path=c['path'], domain=c['domain'])

		pickle.dump(browser.get_cookies() , open("walmart_cookies.pkl","wb"))

		if close_window_after:
			browser.quit()

	def is_captcha(self, text):
		return '<div class="re-captcha">' in text




import os, sys, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


class LinksProcessing:
	def __init__(self):
		self.checkout_url = 'https://www.supremenewyork.com/checkout'

	def process_links(self, url):
		print("process link : " + str(url))
		# https://chromedriver.storage.googleapis.com/index.html?path=87.0.4280.88/
		self.webdriver_path="E:\\Program\\chromedriver.exe"

		# check link is active or sold-out
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		results = soup.find(id='add-remove-buttons')
		print("result : " + str(results))
		if str(results).find('sold-out') != -1:
			print('This product is sold-out')
			self.driver.close()
			return False, 'sold-out'

		self.driver = webdriver.Chrome(executable_path=self.webdriver_path)
		#  add to cart
		self.driver.get(url)
		add_button= self.driver.find_element_by_name('commit')
		add_button.click()
		delay = 3

		# TODO : validate add to cart successful
		# Check out
		self.driver.find_element_by_xpath("//a[contains(@href,'https://www.supremenewyork.com/checkout')]").click()
		delay = 3 # seconds

		self.driver.find_element_by_name('order[billing_name]').send_keys('Tran Ngoc Phong')
		self.driver.find_element_by_name('order[email]').send_keys('phongtran0715@gmail.com')
		self.driver.find_element_by_name('order[tel]').send_keys('0984626619')
		self.driver.find_element_by_name('order[billing_zip]').send_keys('72201')
		self.driver.find_element_by_name('order[billing_state]').send_keys('NY')
		self.driver.find_element_by_name('order[billing_city]').send_keys('NY')
		self.driver.find_element_by_name('order[billing_address]').send_keys('Address')
		self.driver.find_element_by_name('credit_card[type]').send_keys('Visa')
		self.driver.find_element_by_name('riearmxa').send_keys('123456')

		month_select = Select(self.driver.find_element_by_name('credit_card[month]'))
		month_select.select_by_index(3)

		year_select = Select(self.driver.find_element_by_name('credit_card[year]'))
		year_select.select_by_index(3)

		self.driver.find_element_by_name('credit_card[meknk]').send_keys('123')
		self.driver.find_elements_by_class_name('iCheck-helper')[1].click()
		self.driver.find_element_by_name('commit').click()

		delay = 3 # seconds
		# TODO : validate checkout successful
		self.driver.close()
		return True, 'Success'





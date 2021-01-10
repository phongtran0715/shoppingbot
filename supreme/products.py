import os, sys, requests
from bs4 import BeautifulSoup
from selenium import webdriver


class Productions:
	def __init__(self):
		self.checkout_url = 'https://www.supremenewyork.com/checkout'
		self.webdriver_path="C:\\Users\\anhphong\\Downloads\\chromedriver.exe"

	def add_to_cart(self, url):
		# check link is active or sold-out
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		results = soup.find(id='add-remove-buttons')
		if content.find('sold-out') != -1 or content.find('sold out') != -1:
			print('This product is sold-out')
			return

	def checkout(self):
		driver = webdriver.Chrome(executable_path=self.webdriver_path)
		driver.get(self.checkout_url)


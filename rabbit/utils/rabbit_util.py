try:
	from Crypto import Random
	from Crypto.Cipher import AES
except:
	from Cryptodome import Random
	from Cryptodome.Cipher import AES
from colorama import init, Fore
from datetime import datetime
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from notification.webhook import DiscordWebhook, DiscordEmbed
from chromedriver_py import binary_path as driver_path
import json, platform, random, threading, hashlib, base64, string, re
import logging
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

from model.proxy_model import ProxyModel
from model.account_model import AccountModel
from model.profile_model import ProfileModel
from model.task_model import TaskModel
from configparser import ConfigParser


class Encryption:
	def encrypt(self, msg):
		IV = Random.new().read(BLOCK_SIZE)
		aes = AES.new(self.trans(e_key), AES.MODE_CFB, IV)
		return base64.b64encode(IV + aes.encrypt(msg.encode("utf-8")))

	def decrypt(self, msg):
		msg = base64.b64decode(msg)
		IV = msg[:BLOCK_SIZE]
		aes = AES.new(self.trans(e_key), AES.MODE_CFB, IV)
		return aes.decrypt(msg[BLOCK_SIZE:])

	def trans(self, key):
		return hashlib.md5(key).digest()

class RabbitUtil():
	@staticmethod
	def get_profile(profile_name, db_conn):
		if profile_name is None or profile_name == "":
			return None
		query = QSqlQuery("SELECT * FROM profile WHERE profile_name = '" + profile_name + "'", db_conn)
		if query.next():
			billing_profile_model = ProfileModel(str(query.value(0)), query.value(1),query.value(2),query.value(3),
									query.value(4),query.value(5),query.value(6),query.value(7),
									query.value(8), query.value(9),query.value(10),query.value(11),
									query.value(12),query.value(13),query.value(14),query.value(15),
									query.value(16), query.value(17),query.value(18),query.value(19),
									query.value(20),query.value(21),query.value(22),query.value(23),
									query.value(24), query.value(25),query.value(26),query.value(27))
			return billing_profile_model
		return None

	@staticmethod
	def get_proxy(proxy_name, db_conn):
		if proxy_name is None or proxy_name == "":
			return None
		query = QSqlQuery("SELECT content FROM proxies WHERE name = '" + proxy_name + "'", db_conn)
		if query.next():
			proxies = (str(query.value(0)).splitlines())
			print("jack | proxies = {}".format(proxies))
			return RabbitUtil.format_proxy(random.choice(proxies))
		else:
			print("jack | not found proxies")
		return None

	@staticmethod
	def get_proxy_raw(proxy_name, db_conn):
		if proxy_name is None or proxy_name == "":
			return None
		query = QSqlQuery("SELECT content FROM proxies WHERE name = '" + proxy_name + "'", db_conn)
		if query.next():
			proxies = (str(query.value(0)).splitlines())
			return random.choice(proxies)
		return None

	@staticmethod
	def get_account(account_name, db_conn):
		if account_name is None or account_name == "":
			return None
		query = QSqlQuery("SELECT * FROM account WHERE name = '" + account_name + "'", db_conn)
		if query.next():
			account_model = AccountModel(str(query.value(0)), query.value(1), query.value(2),
				query.value(3), query.value(4), query.value(5), query.value(6))
			return account_model
		return None

	@staticmethod
	def get_proxy_by_account(account_name, db_conn):
		if account_name is None or account_name == "":
			return None
		query = QSqlQuery("SELECT proxy FROM account WHERE name = '" + account_name + "'", db_conn)
		if query.next():
			proxy_name = str(query.value(0))
			return RabbitUtil.get_proxy(proxy_name, db_conn)
		return None

	@staticmethod
	def get_profile_by_account(account_name, db_conn):
		if account_name is None or account_name == "":
			return None
		query = QSqlQuery("SELECT billing_profile FROM account WHERE name = '" + account_name + "'", db_conn)
		if query.next():
			profile_name = str(query.value(0))
			return RabbitUtil.get_profile(profile_name, db_conn)
		return None    

	@staticmethod
	def format_proxy(proxy):
		try:
			proxy_parts = proxy.split(":")
			ip, port, user, passw = proxy_parts[0], proxy_parts[1], proxy_parts[2], proxy_parts[3]
			return {
				"http": "http://{}:{}@{}:{}".format(user, passw, ip, port),
				"https": "https://{}:{}@{}:{}".format(user, passw, ip, port)
			}
		except IndexError:
			return {"http": "http://" + proxy, "https": "https://" + proxy}

	@staticmethod
	def send_webhook(webhook_type, site, profile, task_id, image_url):
		self.config = ConfigParser()
		self.config.read(os.path.join('data', 'config.ini'))
		if config.get('notification', 'webhook') is not None and config.get('notification', 'webhook') != "":
			webhook = DiscordWebhook(url=config.get('notification', 'webhook'), username="Rabbit Bot",
									 avatar_url="https://i.imgur.com/60G42xE.png")
			if webhook_type == "OP":
				if config.getint('notification', 'order_placed') == 0:
					return
				embed = DiscordEmbed(title="Order Placed", color=0x34c693)
			elif webhook_type == "B":
				if config.getint('notification', 'browser_opened') == 0:
					return
				embed = DiscordEmbed(title="Complete Order in Browser", color=0xf2a689)
			elif webhook_type == "PF":
				if config.getint('notification', 'payment_failed') == 0:
					return
				embed = DiscordEmbed(title="Payment Failed", color=0xfc5151)
			embed.set_footer(text="Via Bird Bot", icon_url="https://i.imgur.com/60G42xE.png")
			embed.add_embed_field(name="Site", value=site, inline=True)
			embed.add_embed_field(name="Account", value=profile, inline=True)
			embed.add_embed_field(name="Task ID", value=task_id, inline=True)
			embed.set_thumbnail(url=image_url)
			webhook.add_embed(embed)
			try:
				webhook.execute()
			except:
				pass

	@staticmethod
	def random_delay(delay, start, stop):
		"""
		Returns the delay argument combined with a random number between start
		and stop dividied by 1000.
		"""
		return delay + (random.randint(int(start), int(stop)) / 1000)

	@staticmethod
	def create_msg(msg, status, task_id):
		return {"task_id": task_id, "message": msg, "status": status}
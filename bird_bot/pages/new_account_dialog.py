import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from utils import return_data,write_data,get_profile,Encryption


class NewAccount(QtWidgets.QDialog):
	def __init__(self, mode='new', account_name=None):
		super(NewAccount, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "ui", "new_account.ui"), self)
		self.center()
		self.mode = mode
		self.account_name = account_name
		self.init_data()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def init_data(self):
		proxies = return_data("./data/proxies.json")
		for proxy in proxies:
			self.cbProxy.addItem(proxy['list_name'])

		profiles = return_data("./data/profiles.json")
		for profile in profiles:
			self.cbProfile.addItem(profile['profile_name'])

	def load_edit_data(self):
		accounts = return_data("./data/accounts.json")
		for account in accounts:
			if account['name'] == self.account_name:
				index = self.cbType.findText(account['account_type'], QtCore.Qt.MatchFixedString)
				if index >= 0:
					self.cbType.setCurrentIndex(index)

				self.txtName.setText(account['name'])
				self.txtUsername.setText(account['user_name'])
				self.txtPassword.setText(account['password'])

				index = self.cbProxy.findText(account['proxy'], QtCore.Qt.MatchFixedString)
				if index >= 0:
					self.cbProxy.setCurrentIndex(index)

				index = self.cbProfile.findText(account['profile'], QtCore.Qt.MatchFixedString)
				if index >= 0:
					self.cbProfile.setCurrentIndex(index)

	def update_account(self):
		account_data = {
			'account_type' : self.cbType.currentText(),
			'name' : self.txtName.text(),
			'user_name' : self.txtUsername.text(),
			'password' : self.txtPassword.text(),
			'proxy' : self.cbProxy.currentText(),
			'profile' : self.cbProfile.currentText()
		}
		accounts = return_data("./data/accounts.json")
		for account in accounts:
			if account['name'] == self.txtName.text():
				accounts.remove(account)

		accounts.append(account_data)
		write_data("./data/accounts.json",accounts)

	def save_account(self):
		account_data = {
			'account_type' : self.cbType.currentText(),
			'name' : self.txtName.text(),
			'user_name' : self.txtUsername.text(),
			'password' : self.txtPassword.text(),
			'proxy' : self.cbProxy.currentText(),
			'profile' : self.cbProfile.currentText()
		}
		accounts = return_data("./data/accounts.json")
		accounts.append(account_data)
		write_data("./data/accounts.json",accounts)
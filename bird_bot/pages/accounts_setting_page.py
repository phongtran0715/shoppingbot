import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from pages.new_account_page import NewAccount
from model.account_model import AccountModel
from utils import return_data,write_data,get_profile,Encryption


class AccountsManager(QtWidgets.QMainWindow):
	def __init__(self):
		super(AccountsManager, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "ui", "account_manager.ui"), self)
		self.center()

		# create connection for button
		self.btnAdd.clicked.connect(self.btnAdd_clicked)
		self.btnEdit.clicked.connect(self.btnEdit_clicked)
		self.btnDelete.clicked.connect(self.btnDelete_clicked)

		self.load_account_data()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def load_account_data(self):
		self.tbAccount.setRowCount(0)
		accounts = return_data("./data/accounts.json")
		for account in accounts:
			row_count = self.tbAccount.rowCount()
			self.tbAccount.setRowCount(row_count + 1)
			self.tbAccount.setItem(row_count, 0, QTableWidgetItem(account['account_type']))
			self.tbAccount.setItem(row_count, 1, QTableWidgetItem(account['name']))
			self.tbAccount.setItem(row_count, 2, QTableWidgetItem(account['user_name']))
			self.tbAccount.setItem(row_count, 3, QTableWidgetItem(account['password']))
			self.tbAccount.setItem(row_count, 4, QTableWidgetItem(account['proxy']))
			self.tbAccount.setItem(row_count, 5, QTableWidgetItem(account['profile']))

	def btnAdd_clicked(self):
		self.createAccountFrm = NewAccount()
		if self.createAccountFrm.exec_() == QtWidgets.QDialog.Accepted:
			self.createAccountFrm.save_account()
			self.load_account_data()

	def btnEdit_clicked(self):
		index = self.tbAccount.currentRow()
		if index >= 0:
			account_name = self.tbAccount.item(index, 1).text()
			self.editAccountFrm = NewAccount('modify', account_name)
			self.editAccountFrm.load_edit_data()
			if self.editAccountFrm.exec_() == QtWidgets.QDialog.Accepted:
				self.editAccountFrm.update_account()
				self.load_account_data()
		else:
			QMessageBox.critical(self, "Birdbot", 'You must select one account!',)

	def btnDelete_clicked(self):
		index = self.tbAccount.currentRow()
		if index >= 0:
			account_name = self.tbAccount.item(index, 1).text()
			accounts = return_data("./data/accounts.json")
			for account in accounts:
				if account['name'] == account_name:
					accounts.remove(account)
			write_data("./data/accounts.json",accounts)
			self.load_account_data()
		else:
			QMessageBox.critical(self, "Birdbot", 'You must select one account!',)
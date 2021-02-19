import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from pages.new_account_page import NewAccount

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

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def btnAdd_clicked(self):
		self.createAccountFrm = NewAccount()
		if self.createAccountFrm.exec_() == QtWidgets.QDialog.Accepted:
			pass

	def btnEdit_clicked(self):
		index = self.tbAccount.currentRow()
		if index >= 0:
			account_name = self.tbAccount.item(index, 0).text()
			self.editAccountFrm = NewAccount('modify', account_name)
			self.editAccountFrm.loadEditData()
			if self.editAccountFrm.exec_() == QtWidgets.QDialog.Accepted:
				pass
		else:
			QMessageBox.critical(self, "Birdbot", 'You must select one account!',)

	def btnDelete_clicked(self):
		index = self.tbAccount.currentRow()
		if index >= 0:
			account_name = self.tbAccount.item(index, 0).text()
			pass

		else:
			QMessageBox.critical(self, "Birdbot", 'You must select one account!',)
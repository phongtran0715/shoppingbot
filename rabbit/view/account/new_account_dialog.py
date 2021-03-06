import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from utils.rabbit_util import RabbitUtil
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.ui.new_account_dialog import Ui_Dialog

from resource import source


class NewAccount(QtWidgets.QDialog):
	def __init__(self, modifyMode=False, account_id=None):
		super(NewAccount, self).__init__()
		self.db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
		dirname = os.path.dirname(__file__)
		# uic.loadUi(os.path.join(dirname, "../ui", "new_account.ui"), self)
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)
		
		self.center()
		self.account_id = account_id
		self.init_data()
		if modifyMode is True:
			self.load_edit_data()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())


	def init_data(self):
		query = QSqlQuery("SELECT id, profile_name FROM profile", self.db_conn)
		while query.next():
			self.ui.cbProfile.addItem(query.value(1))

		query = QSqlQuery("SELECT id, name FROM proxies", self.db_conn)
		while query.next():
			self.ui.cbProxy.addItem(query.value(1))

	def load_edit_data(self):
		query = QSqlQuery("SELECT * FROM account WHERE id = " + str(self.account_id), self.db_conn)
		if query.next():
			index = self.ui.cbSite.findText(query.value(1), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbSite.setCurrentIndex(index)

			self.ui.txtName.setText(query.value(2))
			self.ui.txtUsername.setText(query.value(3))
			self.ui.txtPassword.setText(query.value(4))

			index = self.ui.cbProxy.findText(query.value(5), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbProxy.setCurrentIndex(index)

			index = self.ui.cbProfile.findText(query.value(6), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbProfile.setCurrentIndex(index)

	def update_account(self):
		query = QSqlQuery(self.db_conn)
		query.prepare(
				"""
				UPDATE account SET 
					site = ?,
					name = ?,
					user_name = ?,
					password = ?,
					proxy = ?,
					billing_profile = ? 
				WHERE id = ?
				"""
			)
		query.addBindValue(self.ui.cbSite.currentText())

		query.addBindValue(self.ui.txtName.text())
		query.addBindValue(self.ui.txtUsername.text())
		query.addBindValue(self.ui.txtPassword.text())
		query.addBindValue(self.ui.cbProxy.currentText())
		query.addBindValue(self.ui.cbProfile.currentText())
		query.addBindValue(str(self.account_id))
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			self.close()

	def create_account(self):
		query = QSqlQuery(self.db_conn)
		query.prepare(
				"""
				INSERT INTO account (
					site,
					name,
					user_name,
					password,
					proxy,
					billing_profile
				)
				VALUES (?, ?, ?, ?, ?, ?)
				"""
			)
		query.addBindValue(self.ui.cbSite.currentText())

		query.addBindValue(self.ui.txtName.text())
		query.addBindValue(self.ui.txtUsername.text())
		query.addBindValue(self.ui.txtPassword.text())
		query.addBindValue(self.ui.cbProxy.currentText())
		query.addBindValue(self.ui.cbProfile.currentText())
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			self.close()
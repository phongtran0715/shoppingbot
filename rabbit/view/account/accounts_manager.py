import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.account.new_account_dialog import NewAccount


class AccountManager(QtWidgets.QMainWindow):
	def __init__(self):
		super(AccountManager, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "../ui", "account_manager.ui"), self)
		self.center()

		self.db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
		
		# create connection for button
		self.btnAdd.clicked.connect(self.btnAdd_clicked)
		self.btnEdit.clicked.connect(self.btnEdit_clicked)
		self.btnDelete.clicked.connect(self.btnDelete_clicked)
		self.btnDeleteAll.clicked.connect(self.btnDeleteAll_clicked)

		self.tbAccount.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tbAccount.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.tbAccount.setColumnHidden(0, True);
		self.setFixedSize(915, 409)

		self.loadAccountData()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadAccountData(self):
		self.tbAccount.setRowCount(0)
		query = QSqlQuery("SELECT * FROM account", self.db_conn)
		while query.next():
			rows = self.tbAccount.rowCount()
			self.tbAccount.setRowCount(rows + 1)
			self.tbAccount.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
			self.tbAccount.setItem(rows, 1, QTableWidgetItem(query.value(1)))
			self.tbAccount.setItem(rows, 2, QTableWidgetItem(query.value(2)))
			self.tbAccount.setItem(rows, 3, QTableWidgetItem(query.value(3)))
			self.tbAccount.setItem(rows, 4, QTableWidgetItem(query.value(4)))
			self.tbAccount.setItem(rows, 5, QTableWidgetItem(query.value(5)))
			self.tbAccount.setItem(rows, 6, QTableWidgetItem(query.value(6)))

	def btnAdd_clicked(self):
		self.create_account_frm = NewAccount()
		if self.create_account_frm.exec_() == QtWidgets.QDialog.Accepted:
			self.create_account_frm.create_account()
			self.loadAccountData()

	def btnEdit_clicked(self):
		index = self.tbAccount.currentRow()
		if index >= 0:
			account_id = self.tbAccount.item(index, 0).text()
			self.edit_account_frm = NewAccount(True, account_id)
			if self.edit_account_frm.exec_() == QtWidgets.QDialog.Accepted:
				self.edit_account_frm.update_account()
				self.loadAccountData()
		else:
			QMessageBox.critical(self, "Rabbit", 'You must select one account!',)

	def btnDelete_clicked(self):
		index = self.tbAccount.currentRow()
		if index >= 0:
			account_id = self.tbAccount.item(index, 0).text()
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM account WHERE id = ?")
			query.addBindValue(account_id)
			if not query.exec():
				QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
			else:
				self.loadAccountData()
		else:
			QMessageBox.critical(self, "Rabbit - Error!", 'You must select one account to delete!',)

	def btnDeleteAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to delete all account?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM account")
			if not query.exec():
				QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
			else:
				self.loadAccountData()

	def __exit__(self, exc_type, exc_val, exc_tb):
		print("__exit__")
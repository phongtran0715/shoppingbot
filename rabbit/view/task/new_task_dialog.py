import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.ui.new_task_dialog import Ui_Dialog


class NewTask(QtWidgets.QDialog):
	def __init__(self, modifyMode=False, task_id=None, parent=None):
		super(NewTask, self).__init__()
		self.db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
		dirname = os.path.dirname(__file__)
		# uic.loadUi(os.path.join(dirname, "../ui", "new_task_dialog.ui"), self)
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)

		self.task_id = task_id
		self.parent = parent
		self.init_data()
		if modifyMode is True:
			self.load_data()
		self.show()
		self.center()

		self.onlyInt = QtGui.QIntValidator()
		self.ui.txtMaxPrice.setValidator(self.onlyInt)
		self.ui.txtMaxQuantity.setValidator(self.onlyInt)
		self.ui.txtMonitorDelay.setValidator(self.onlyInt)
		self.ui.txtErrorDelay.setValidator(self.onlyInt)

		# create signal for button
		self.ui.btnAccountAdd.clicked.connect(self.btnAccountAddClicked)
		self.ui.txtLink.textChanged.connect(self.txtLinkChanged)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def init_data(self):
		query = QSqlQuery("SELECT id, name FROM proxies", self.db_conn)
		while query.next():
			self.ui.cbMonitorProxy.addItem(query.value(1))

		query = QSqlQuery("SELECT id, name FROM account", self.db_conn)
		while query.next():
			self.ui.cbAccount.addItem(query.value(1))

	def load_data(self):
		query = QSqlQuery("""
			SELECT product, site, monitor_proxy, monitor_delay, error_delay, max_price, max_quantity, account 
			FROM task WHERE id = """ + str(self.task_id), self.db_conn)
		if query.next():
			self.ui.txtLink.setText(query.value(0))

			index = self.ui.cbSite.findText(query.value(1), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbSite.setCurrentIndex(index)

			index = self.ui.cbMonitorProxy.findText(query.value(2), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbMonitorProxy.setCurrentIndex(index)

			self.ui.txtMonitorDelay.setText(str(query.value(3)))
			self.ui.txtErrorDelay.setText(str(query.value(4)))
			self.ui.txtMaxPrice.setText(str(query.value(5)))
			self.ui.txtMaxQuantity.setText(str(query.value(6)))
			self.ui.txtAccount.setText(query.value(7))

			self.txtLinkChanged()

	def create_task(self):
		query = QSqlQuery(self.db_conn)
		query.prepare(""" INSERT INTO task (product, site, monitor_proxy, monitor_delay, error_delay, 
			max_price, max_quantity, account) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""")
		query.addBindValue(self.ui.txtLink.text())
		query.addBindValue(self.ui.cbSite.currentText())
		query.addBindValue(self.ui.cbMonitorProxy.currentText())
		query.addBindValue(int(self.ui.txtMonitorDelay.text()))
		query.addBindValue(int(self.ui.txtErrorDelay.text()))
		query.addBindValue(int(self.ui.txtMaxPrice.text()))
		query.addBindValue(int(self.ui.txtMaxQuantity.text()))
		query.addBindValue(self.ui.txtAccount.text())
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			# add new row to table
			last_inserted_id = query.lastInsertId()
			rowPosition = self.parent.ui.tbListTask.rowCount()
			self.parent.ui.tbListTask.insertRow(rowPosition)
			self.parent.ui.tbListTask.setItem(rowPosition , 0, QTableWidgetItem(str(last_inserted_id)))
			self.parent.ui.tbListTask.setItem(rowPosition , 1, QTableWidgetItem(self.ui.cbSite.currentText()))
			self.parent.ui.tbListTask.setItem(rowPosition , 2, QTableWidgetItem(self.ui.txtLink.text()))
			self.parent.ui.tbListTask.setItem(rowPosition , 3, QTableWidgetItem(self.ui.txtAccount.text()))
			self.close()

	def update_task(self):
		query = QSqlQuery(self.db_conn)
		query.prepare(""" UPDATE task SET product = ?, site = ?, monitor_proxy = ?, monitor_delay = ?, error_delay = ?, 
			max_price = ? , max_quantity = ? , account = ? WHERE id = ?""")
		query.addBindValue(self.ui.txtLink.text())
		query.addBindValue(self.ui.cbSite.currentText())
		query.addBindValue(self.ui.cbMonitorProxy.currentText())
		query.addBindValue(self.ui.txtMonitorDelay.text())
		query.addBindValue(self.ui.txtErrorDelay.text())
		query.addBindValue(self.ui.txtMaxPrice.text())
		query.addBindValue(self.ui.txtMaxQuantity.text())
		query.addBindValue(self.ui.txtAccount.text())
		query.addBindValue(self.task_id)
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			# udpate table
			row = self.parent.ui.tbListTask.currentRow()
			self.parent.ui.tbListTask.item(row, 1).setText(self.ui.cbSite.currentText())
			self.parent.ui.tbListTask.item(row, 2).setText(self.ui.txtLink.text())
			self.parent.ui.tbListTask.item(row, 3).setText(self.ui.txtAccount.text())
			self.close()

	def btnAccountAddClicked(self):
		account = self.txtAccount.text()
		if account is None or account == "":
			account += self.ui.cbAccount.currentText()
		else:
			account += "," + self.ui.cbAccount.currentText()

		self.ui.txtAccount.setText(account)

	def txtLinkChanged(self):
		product = self.ui.txtLink.text()
		if "gamestop" in product:
			index = self.ui.cbSite.findText("GameStop", QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbSite.setCurrentIndex(index)

				self.ui.cbAccount.clear()
				query = QSqlQuery("SELECT id, name FROM account WHERE site = 'GameStop'", self.db_conn)
				while query.next():
					self.ui.cbAccount.addItem(query.value(1))
		elif "walmart" in product:
			index = self.ui.cbSite.findText("Walmart", QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbSite.setCurrentIndex(index)

				self.ui.cbAccount.clear()
				query = QSqlQuery("SELECT id, name FROM account WHERE site = 'Walmart'", self.db_conn)
				while query.next():
					self.ui.cbAccount.addItem(query.value(1))
		elif "bestbuy" in product:
			index = self.ui.cbSite.findText("Bestbuy", QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbSite.setCurrentIndex(index)

				self.ui.cbAccount.clear()
				query = QSqlQuery("SELECT id, name FROM account WHERE site = 'Bestbuy'", self.db_conn)
				while query.next():
					self.ui.cbAccount.addItem(query.value(1))
		elif "target" in product:
			index = self.ui.cbSite.findText("Target", QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbSite.setCurrentIndex(index)

				self.ui.cbAccount.clear()
				query = QSqlQuery("SELECT id, name FROM account WHERE site = 'Target'", self.db_conn)
				while query.next():
					self.ui.cbAccount.addItem(query.value(1))
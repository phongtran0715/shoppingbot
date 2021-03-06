import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from utils.rabbit_util import RabbitUtil
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.ui.new_proxy_dialog import Ui_Dialog


class NewProxy(QtWidgets.QDialog):
	def __init__(self, modifyMode=False, proxy_id=None):
		super(NewProxy, self).__init__()
		self.db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
		dirname = os.path.dirname(__file__)
		# uic.loadUi(os.path.join(dirname, "../ui", "new_proxy_dialog.ui"), self)
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)

		self.center()
		self.modifyMode = modifyMode
		self.proxy_id = proxy_id
		if modifyMode is True:
			self.load_edit_data()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def load_edit_data(self):
		query = QSqlQuery("SELECT name, content FROM proxies WHERE id = " + str(self.proxy_id), self.db_conn)
		if query.next():
			self.ui.txtName.setText(query.value(0))
			self.ui.txtContent.setPlainText(query.value(1))

	def update_proxy(self):
		query = QSqlQuery(self.db_conn)
		query.prepare("UPDATE proxies SET name = ?, content = ? WHERE id = ?")
		query.addBindValue(self.ui.txtName.text())
		query.addBindValue(self.ui.txtContent.toPlainText())
		query.addBindValue(int(self.proxy_id))
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().databaseText(),)
		else:
			self.close()

	def create_proxy(self):
		query = QSqlQuery(self.db_conn)
		query.prepare("INSERT INTO proxies (name, content) VALUES (?, ?)")
		query.addBindValue(self.ui.txtName.text())
		query.addBindValue(self.ui.txtContent.toPlainText())
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().databaseText(),)
		else:
			self.close()
		
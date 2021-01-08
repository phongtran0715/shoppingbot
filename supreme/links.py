from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import os


class LinkManager(QtWidgets.QMainWindow):
	def __init__(self, mode='new', link_id=None):
		super(LinkManager, self).__init__()
		uic.loadUi(os.path.join("ui", "new_link.ui"), self)
		self.center()
		self.mode = mode
		self.link_id = link_id
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
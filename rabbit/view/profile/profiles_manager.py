import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.profile.new_profile import NewProfile
from view.ui.billing_profile_manager import Ui_formProfileManager
from resource import source


class ProfileManager(QtWidgets.QMainWindow):
	def __init__(self):
		super(ProfileManager, self).__init__()
		dirname = os.path.dirname(__file__)
		# uic.loadUi(os.path.join(dirname, "../ui", "billing_profile_manager.ui"), self)
		self.ui = Ui_formProfileManager()
		self.ui.setupUi(self)
		self.center()

		self.db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
		
		# # create connection for button
		self.ui.btnAdd.clicked.connect(self.btnAdd_clicked)
		self.ui.btnEdit.clicked.connect(self.btnEdit_clicked)
		self.ui.btnDelete.clicked.connect(self.btnDelete_clicked)
		self.ui.btnDeleteAll.clicked.connect(self.btnDeleteAll_clicked)

		self.ui.tbProfile.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.ui.tbProfile.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.ui.tbProfile.setColumnHidden(0, True);
		self.setFixedSize(806, 416)

		self.loadProfileData()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadProfileData(self):
		self.ui.tbProfile.setRowCount(0)
		query = QSqlQuery("SELECT id, profile_name FROM profile", self.db_conn)
		while query.next():
			rows = self.ui.tbProfile.rowCount()
			self.ui.tbProfile.setRowCount(rows + 1)
			self.ui.tbProfile.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
			self.ui.tbProfile.setItem(rows, 1, QTableWidgetItem(query.value(1)))

	def btnAdd_clicked(self):
		self.createProfileFrm = NewProfile()
		if self.createProfileFrm.exec_() == QtWidgets.QDialog.Accepted:
			self.createProfileFrm.create_profile()
			self.loadProfileData()

	def btnEdit_clicked(self):
		index = self.ui.tbProfile.currentRow()
		if index >= 0:
			profile_id = self.ui.tbProfile.item(index, 0).text()
			self.editProfileFrm = NewProfile(True, profile_id)
			if self.editProfileFrm.exec_() == QtWidgets.QDialog.Accepted:
				self.editProfileFrm.update_profile()
				self.loadProfileData()
		else:
			QMessageBox.critical(self, "Rabbit", 'You must select one profile!',)

	def btnDelete_clicked(self):
		index = self.ui.tbProfile.currentRow()
		if index >= 0:
			profile_id = self.ui.tbProfile.item(index, 0).text()
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM profile WHERE id = ?")
			query.addBindValue(profile_id)
			if not query.exec():
				QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % self.query.lastError().databaseText(),)
			else:
				self.loadProfileData()
		else:
			QMessageBox.critical(self, "Rabbit - Error!", 'You must select one profile to delete!',)

	def btnDeleteAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to delete all profile?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM profile")
			if not query.exec():
				QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % self.query.lastError().databaseText(),)
			else:
				self.loadProfileData()

	def __exit__(self, exc_type, exc_val, exc_tb):
		print("__exit__")
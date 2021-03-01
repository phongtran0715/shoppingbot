import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.profile.new_profile import NewProfile


class ProfileManager(QtWidgets.QMainWindow):
	def __init__(self):
		super(ProfileManager, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "../ui", "billing_profile_manager.ui"), self)
		self.center()

		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		
		# # create connection for button
		self.btnAdd.clicked.connect(self.btnAdd_clicked)
		self.btnEdit.clicked.connect(self.btnEdit_clicked)
		self.btnDelete.clicked.connect(self.btnDelete_clicked)
		self.btnDeleteAll.clicked.connect(self.btnDeleteAll_clicked)

		self.tbProfile.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tbProfile.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.tbProfile.setColumnHidden(0, True);

		self.loadProfileData()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadProfileData(self):
		self.tbProfile.setRowCount(0)
		query = QSqlQuery("SELECT id, profile_name FROM profile", self.db_conn)
		while query.next():
			rows = self.tbProfile.rowCount()
			self.tbProfile.setRowCount(rows + 1)
			self.tbProfile.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
			self.tbProfile.setItem(rows, 1, QTableWidgetItem(query.value(1)))

	def btnAdd_clicked(self):
		self.createProfileFrm = NewProfile()
		if self.createProfileFrm.exec_() == QtWidgets.QDialog.Accepted:
			self.createProfileFrm.create_profile()
			self.loadProfileData()

	def btnEdit_clicked(self):
		index = self.tbProfile.currentRow()
		if index >= 0:
			profile_id = self.tbProfile.item(index, 0).text()
			self.editProfileFrm = NewProfile(True, profile_id)
			if self.editProfileFrm.exec_() == QtWidgets.QDialog.Accepted:
				self.editProfileFrm.update_profile()
				self.loadProfileData()
		else:
			QMessageBox.critical(self, "Rabbit", 'You must select one profile!',)

	def btnDelete_clicked(self):
		index = self.tbProfile.currentRow()
		if index >= 0:
			profile_id = self.tbProfile.item(index, 0).text()
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
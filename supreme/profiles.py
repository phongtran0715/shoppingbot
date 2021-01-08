from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import os


class ProfileManager(QtWidgets.QMainWindow):
	def __init__(self):
		super(ProfileManager, self).__init__()
		uic.loadUi(os.path.join("ui", "profile_manager.ui"), self)
		self.center()

		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		print(self.db_conn.isOpen())
		
		# create connection for button
		self.btnAdd.clicked.connect(self.btnAdd_clicked)
		self.btnEdit.clicked.connect(self.btnEdit_clicked)
		self.btnDelete.clicked.connect(self.btnDelete_clicked)
		self.btnDeleteAll.clicked.connect(self.btnDeleteAll_clicked)

		self.tbProfile.setHorizontalHeaderLabels(["ID", "NAME", "EMAIL", "PHONE", "CARD TYPE"])
		self.tbProfile.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tbProfile.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

		self.loadProfileData()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadProfileData(self):
		self.tbProfile.setRowCount(0)
		query = QSqlQuery("SELECT * FROM profile", self.db_conn)
		while query.next():
			rows = self.tbProfile.rowCount()
			self.tbProfile.setRowCount(rows + 1)
			self.tbProfile.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
			self.tbProfile.setItem(rows, 1, QTableWidgetItem(query.value(1)))
			self.tbProfile.setItem(rows, 2, QTableWidgetItem(query.value(2)))
			self.tbProfile.setItem(rows, 3, QTableWidgetItem(query.value(3)))
			self.tbProfile.setItem(rows, 4, QTableWidgetItem(query.value(15)))

	def btnAdd_clicked(self):
		self.createProfileFrm = CreateProfileWindown()
		self.createProfileFrm.show()
		self.loadProfileData()

	def btnEdit_clicked(self):
		index = self.tbProfile.currentRow()
		self.editProfileFrm = CreateProfileWindown()
		self.editProfileFrm.show()
		self.loadProfileData()

	def btnDelete_clicked(self):
		index = self.tbProfile.currentRow()
		if index >= 0:
			profile_id = self.tbProfile.item(index, 0).text()
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM profile WHERE id = ?")
			query.addBindValue(profile_id)
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.db_conn.lastError().databaseText(),)
			else:
				self.loadProfileData()
		else:
			QMessageBox.critical(self, "Supreme - Error!", 'You must select one profile to delete!',)

	def btnDeleteAll_clicked(self):
		ret = QMessageBox.question(self, 'MessageBox', "Do you want to delete all profile?", QMessageBox.Yes | QMessageBox.No )
		if ret == QMessageBox.Yes:
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM profile")
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.db_conn.lastError().databaseText(),)
			else:
				self.loadProfileData()

	def __exit__(self, exc_type, exc_val, exc_tb):
		print("__exit__")


class CreateProfileWindown(QtWidgets.QMainWindow):
	def __init__(self):
		super(CreateProfileWindown, self).__init__()
		uic.loadUi(os.path.join("ui", "new_profile.ui"), self)
		self.center()

		# create connection for button
		self.btnCreate.clicked.connect(self.btnCreate_clicked)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def btnCreate_clicked(self):
		pass		
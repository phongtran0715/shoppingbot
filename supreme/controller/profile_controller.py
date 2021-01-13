from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import os


class ProfileController(QtWidgets.QMainWindow):
	def __init__(self):
		super(ProfileController, self).__init__()
		uic.loadUi(os.path.join("view", "profile_manager.ui"), self)
		self.center()

		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		
		# create connection for button
		self.btnAdd.clicked.connect(self.btnAdd_clicked)
		self.btnEdit.clicked.connect(self.btnEdit_clicked)
		self.btnDelete.clicked.connect(self.btnDelete_clicked)
		self.btnDeleteAll.clicked.connect(self.btnDeleteAll_clicked)

		self.tbProfile.setHorizontalHeaderLabels(["ID", "PROFILE NAME", "EMAIL", "PHONE", "CARD TYPE"])
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
		query = QSqlQuery("SELECT * FROM profile", self.db_conn)
		while query.next():
			rows = self.tbProfile.rowCount()
			self.tbProfile.setRowCount(rows + 1)
			self.tbProfile.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
			self.tbProfile.setItem(rows, 1, QTableWidgetItem(query.value(1)))
			self.tbProfile.setItem(rows, 2, QTableWidgetItem(query.value(3)))
			self.tbProfile.setItem(rows, 3, QTableWidgetItem(query.value(4)))
			self.tbProfile.setItem(rows, 4, QTableWidgetItem(query.value(15)))

	def btnAdd_clicked(self):
		self.createProfileFrm = NewProfile()
		if self.createProfileFrm.exec_() == QtWidgets.QDialog.Accepted:
			self.createProfileFrm.updateProfile()
			self.loadProfileData()

	def btnEdit_clicked(self):
		index = self.tbProfile.currentRow()
		if index >= 0:
			profile_id = self.tbProfile.item(index, 0).text()
			self.editProfileFrm = NewProfile('modify', profile_id)
			self.editProfileFrm.loadEditData()
			if self.editProfileFrm.exec_() == QtWidgets.QDialog.Accepted:
				self.editProfileFrm.updateProfile()
				self.loadProfileData()
		else:
			QMessageBox.critical(self, "Supreme", 'You must select one profile!',)

	def btnDelete_clicked(self):
		index = self.tbProfile.currentRow()
		if index >= 0:
			profile_id = self.tbProfile.item(index, 0).text()
			query = QSqlQuery(self.db_conn)
			query.prepare("DELETE FROM profile WHERE id = ?")
			query.addBindValue(profile_id)
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.query.lastError().databaseText(),)
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
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.query.lastError().databaseText(),)
			else:
				self.loadProfileData()

	def __exit__(self, exc_type, exc_val, exc_tb):
		print("__exit__")


class NewProfile(QtWidgets.QDialog):
	def __init__(self, mode='new', profile_id=None):
		super(NewProfile, self).__init__()
		uic.loadUi(os.path.join("view", "new_profile_dialog.ui"), self)
		self.center()
		self.mode = mode
		self.profile_id = profile_id
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadEditData(self):
		query = QSqlQuery("SELECT * FROM profile WHERE id = " + str(self.profile_id), self.db_conn)
		if query.next():
			self.txtProfileName.setText(query.value(1))
			self.txtCardName.setText(query.value(2))
			self.txtEmail.setText(query.value(3))
			self.txtPhone.setText(query.value(4))
			self.txtAddress.setText(query.value(5))
			self.txtAddress2.setText(query.value(6))
			self.txtPostcode.setText(query.value(7))
			self.txtCity.setText(query.value(8))
			self.txtState.setText(query.value(9))
			self.txtCountry.setText(query.value(10))
			self.txtCardNumber.setText(query.value(11))
			
			index = self.cbExpiryMonth.findText(query.value(12), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbExpiryMonth.setCurrentIndex(index)

			index = self.cbExpiryYear.findText(query.value(13), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbExpiryYear.setCurrentIndex(index)
			
			self.txtCvv.setText(query.value(14))
			
			index = self.cbCardType.findText(query.value(15), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbCardType.setCurrentIndex(index)

	def updateProfile(self):
		if self.mode == 'new':
			query = QSqlQuery(self.db_conn)
			query.prepare(
					"""
					INSERT INTO profile (
						profile_name,
						card_name,
						email,
						phone,
						address,
						address_2,
						postcode,
						city,
						state,
						country,
						card_number,
						exp_month,
						exp_year,
						cvv,
						card_type
					)
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
					"""
				)
			query.addBindValue(self.txtProfileName.text())
			query.addBindValue(self.txtCardName.text())
			query.addBindValue(self.txtEmail.text())
			query.addBindValue(self.txtPhone.text())
			query.addBindValue(self.txtAddress.text())
			query.addBindValue(self.txtAddress2.text())
			query.addBindValue(self.txtPostcode.text())
			query.addBindValue(self.txtCity.text())
			query.addBindValue(self.txtState.text())
			query.addBindValue(self.txtCountry.text())
			query.addBindValue(self.txtCardNumber.text())
			query.addBindValue(self.cbExpiryMonth.currentText())
			query.addBindValue(self.cbExpiryYear.currentText())
			query.addBindValue(self.txtCvv.text())
			query.addBindValue(self.cbCardType.currentText())
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.query.lastError().databaseText(),)
			else:
				self.close()
		else:
			query = QSqlQuery(self.db_conn)
			query.prepare(
					"""
					UPDATE profile SET 
						profile_name = ?,
						card_name = ?,
						email = ?,
						phone = ?,
						address = ?,
						address_2 = ?,
						postcode = ?,
						city = ?,
						state = ?,
						country = ?,
						card_number = ?,
						exp_month = ?,
						exp_year = ?,
						cvv = ?,
						card_type  = ?
						WHERE id = ?
					"""
				)
			query.addBindValue(self.txtProfileName.text())
			query.addBindValue(self.txtCardName.text())
			query.addBindValue(self.txtEmail.text())
			query.addBindValue(self.txtPhone.text())
			query.addBindValue(self.txtAddress.text())
			query.addBindValue(self.txtAddress2.text())
			query.addBindValue(self.txtPostcode.text())
			query.addBindValue(self.txtCity.text())
			query.addBindValue(self.txtState.text())
			query.addBindValue(self.txtCountry.text())
			query.addBindValue(self.txtCardNumber.text())
			query.addBindValue(self.cbExpiryMonth.currentText())
			query.addBindValue(self.cbExpiryYear.currentText())
			query.addBindValue(self.txtCvv.text())
			query.addBindValue(self.cbCardType.currentText())
			query.addBindValue(int(self.profile_id))
			if not query.exec():
				QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % self.query.lastError().databaseText(),)
			else:
				self.close()
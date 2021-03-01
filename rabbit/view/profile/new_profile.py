import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


class NewProfile(QtWidgets.QDialog):
	def __init__(self, modifyMode=False, profile_id=None):
		super(NewProfile, self).__init__()
		dirname = os.path.dirname(__file__)
		uic.loadUi(os.path.join(dirname, "../ui", "new_billing_profile_dialog.ui"), self)
		self.center()
		self.db_conn = QSqlDatabase.database("supreme_db_conn", open=False)
		self.modifyMode = modifyMode
		self.profile_id = profile_id
		if modifyMode is True:
			self.loadEditData()

		# connect signal
		self.cbSameAsShipping.stateChanged.connect(self.cbSameAsShippingClicked)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadEditData(self):
		query = QSqlQuery("SELECT * FROM profile WHERE id = " + str(self.profile_id), self.db_conn)
		if query.next():
			self.txtProfileName.setText(query.value(1))
			self.txtShippingFirstName.setText(query.value(2))
			self.txtShippingLastName.setText(query.value(3))
			self.txtShippingEmail.setText(query.value(4))
			self.txtsShippingPhone.setText(query.value(5))
			self.txtShippingAddress1.setText(query.value(6))
			self.txtShippingAddress2.setText(query.value(7))
			self.txtShippingCity.setText(query.value(8))
			self.txtShippingZipcode.setText(query.value(9))
			
			index = self.cbShippingState.findText(query.value(10), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbShippingState.setCurrentIndex(index)

			index = self.cbShippingCountry.findText(query.value(11), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbShippingCountry.setCurrentIndex(index)

			self.txtBillingFirstName.setText(query.value(12))
			self.txtBillingLastName.setText(query.value(13))
			self.txtBillingEmail.setText(query.value(14))
			self.txtsBillingPhone.setText(query.value(15))
			self.txtBillingAddress1.setText(query.value(16))
			self.txtBillingAddress2.setText(query.value(17))
			self.txtBillingCity.setText(query.value(18))
			self.txtBillingZipcode.setText(query.value(19))

			index = self.cbBillingState.findText(query.value(20), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbBillingState.setCurrentIndex(index)

			index = self.cbBillingCountry.findText(query.value(21), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbBillingCountry.setCurrentIndex(index)

			index = self.cbCardType.findText(query.value(22), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbCardType.setCurrentIndex(index)

			self.txtCardName.setText(query.value(23))
			self.txtCardNumber.setText(query.value(24))
			self.txtCvv.setText(query.value(25))

			index = self.cbExpiryMonth.findText(query.value(26), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbExpiryMonth.setCurrentIndex(index)

			index = self.cbExpiryYear.findText(query.value(27), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbExpiryYear.setCurrentIndex(index)

	def create_profile(self):
		query = QSqlQuery(self.db_conn)
		query.prepare(
				"""
				INSERT INTO profile (
					profile_name,
					shipping_first_name,
					shipping_last_name,
					shipping_email,
					shipping_phone,
					shipping_address_1,
					shipping_address_2,
					shipping_city,
					shipping_zipcode,
					shipping_state,
					shipping_country,
					billing_first_name,
					billing_last_name,
					billing_email,
					billing_phone,
					billing_address_1,
					billing_address_2,
					billing_city,
					billing_zipcode,
					billing_state,
					billing_country,
					card_type,
					card_name,
					card_number,
					card_cvv,
					exp_month,
					exp_year
				)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				"""
			)
		query.addBindValue(self.txtProfileName.text())

		query.addBindValue(self.txtShippingFirstName.text())
		query.addBindValue(self.txtShippingLastName.text())
		query.addBindValue(self.txtShippingEmail.text())
		query.addBindValue(self.txtsShippingPhone.text())
		query.addBindValue(self.txtShippingAddress1.text())
		query.addBindValue(self.txtShippingAddress2.text())
		query.addBindValue(self.txtShippingCity.text())
		query.addBindValue(self.txtShippingZipcode.text())
		query.addBindValue(self.cbShippingState.currentText())
		query.addBindValue(self.cbShippingCountry.currentText())

		query.addBindValue(self.txtBillingFirstName.text())
		query.addBindValue(self.txtBillingLastName.text())
		query.addBindValue(self.txtBillingEmail.text())
		query.addBindValue(self.txtsBillingPhone.text())
		query.addBindValue(self.txtBillingAddress1.text())
		query.addBindValue(self.txtBillingAddress2.text())
		query.addBindValue(self.txtBillingCity.text())
		query.addBindValue(self.txtBillingZipcode.text())
		query.addBindValue(self.cbBillingState.currentText())
		query.addBindValue(self.cbBillingCountry.currentText())

		query.addBindValue(self.cbCardType.currentText())
		query.addBindValue(self.txtCardName.text())
		query.addBindValue(self.txtCardNumber.text())
		query.addBindValue(self.txtCvv.text())
		query.addBindValue(self.cbExpiryMonth.currentText())
		query.addBindValue(self.cbExpiryYear.currentText())
		if not query.exec():
			QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			self.close()

	def update_profile(self):
		query = QSqlQuery(self.db_conn)
		query.prepare(
				"""
				UPDATE profile SET 
					profile_name = ?,
					shipping_first_name = ?,
					shipping_last_name = ?,
					shipping_email = ?,
					shipping_phone = ?,
					shipping_address_1 = ?,
					shipping_address_2 = ?,
					shipping_city = ?,
					shipping_zipcode = ?,
					shipping_state = ?,
					shipping_country = ?,
					billing_first_name = ?,
					billing_last_name = ?,
					billing_email = ?,
					billing_phone = ?,
					billing_address_1 = ?,
					billing_address_2 = ?,
					billing_city = ?,
					billing_zipcode = ?,
					billing_state = ?,
					billing_country = ?,
					card_type = ?,
					card_name = ?,
					card_number = ?,
					card_cvv = ?,
					exp_month = ?,
					exp_year = ? 
				WHERE id = ?
				"""
			)
		query.addBindValue(self.txtProfileName.text())

		query.addBindValue(self.txtShippingFirstName.text())
		query.addBindValue(self.txtShippingLastName.text())
		query.addBindValue(self.txtShippingEmail.text())
		query.addBindValue(self.txtsShippingPhone.text())
		query.addBindValue(self.txtShippingAddress1.text())
		query.addBindValue(self.txtShippingAddress2.text())
		query.addBindValue(self.txtShippingCity.text())
		query.addBindValue(self.txtShippingZipcode.text())
		query.addBindValue(self.cbShippingState.currentText())
		query.addBindValue(self.cbShippingCountry.currentText())

		query.addBindValue(self.txtBillingFirstName.text())
		query.addBindValue(self.txtBillingLastName.text())
		query.addBindValue(self.txtBillingEmail.text())
		query.addBindValue(self.txtsBillingPhone.text())
		query.addBindValue(self.txtBillingAddress1.text())
		query.addBindValue(self.txtBillingAddress2.text())
		query.addBindValue(self.txtBillingCity.text())
		query.addBindValue(self.txtBillingZipcode.text())
		query.addBindValue(self.cbBillingState.currentText())
		query.addBindValue(self.cbBillingCountry.currentText())

		query.addBindValue(self.cbCardType.currentText())
		query.addBindValue(self.txtCardName.text())
		query.addBindValue(self.txtCardNumber.text())
		query.addBindValue(self.txtCvv.text())
		query.addBindValue(self.cbExpiryMonth.currentText())
		query.addBindValue(self.cbExpiryYear.currentText())

		query.addBindValue(str(self.profile_id))
		if not query.exec():
			QMessageBox.critical(self, "Supreme - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			self.close()

	def cbSameAsShippingClicked(self,state):
		if state == QtCore.Qt.Checked:
			self.txtBillingFirstName.setText(self.txtShippingFirstName.text())
			self.txtBillingLastName.setText(self.txtShippingLastName.text())
			self.txtBillingEmail.setText(self.txtShippingEmail.text())
			self.txtsBillingPhone.setText(self.txtsShippingPhone.text())
			self.txtBillingAddress1.setText(self.txtShippingAddress1.text())
			self.txtBillingAddress2.setText(self.txtShippingAddress2.text())
			self.txtBillingCity.setText(self.txtShippingCity.text())

			index = self.cbBillingState.findText(self.cbShippingState.currentText(), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbBillingState.setCurrentIndex(index)

			self.txtBillingZipcode.setText(self.txtShippingZipcode.text())

			index = self.cbBillingCountry.findText(self.cbShippingCountry.currentText(), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.cbBillingCountry.setCurrentIndex(index)
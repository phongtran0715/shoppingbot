import os
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from view.ui.new_billing_profile_dialog import Ui_Dialog
from resource import source


class NewProfile(QtWidgets.QDialog):
	def __init__(self, modifyMode=False, profile_id=None):
		super(NewProfile, self).__init__()
		# dirname = os.path.dirname(__file__)
		# uic.loadUi(os.path.join(dirname, "../ui", "new_billing_profile_dialog.ui"), self)
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)

		self.center()
		self.db_conn = QSqlDatabase.database("rabbit_db_conn", open=False)
		self.modifyMode = modifyMode
		self.profile_id = profile_id
		if modifyMode is True:
			self.loadEditData()

		# connect signal
		self.ui.cbSameAsShipping.stateChanged.connect(self.cbSameAsShippingClicked)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def loadEditData(self):
		query = QSqlQuery("SELECT * FROM profile WHERE id = " + str(self.profile_id), self.db_conn)
		if query.next():
			self.ui.txtProfileName.setText(query.value(1))
			self.ui.txtShippingFirstName.setText(query.value(2))
			self.ui.txtShippingLastName.setText(query.value(3))
			self.ui.txtShippingEmail.setText(query.value(4))
			self.ui.txtsShippingPhone.setText(query.value(5))
			self.ui.txtShippingAddress1.setText(query.value(6))
			self.ui.txtShippingAddress2.setText(query.value(7))
			self.ui.txtShippingCity.setText(query.value(8))
			self.ui.txtShippingZipcode.setText(query.value(9))
			
			index = self.ui.cbShippingState.findText(query.value(10), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbShippingState.setCurrentIndex(index)

			index = self.ui.cbShippingCountry.findText(query.value(11), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbShippingCountry.setCurrentIndex(index)

			self.ui.txtBillingFirstName.setText(query.value(12))
			self.ui.txtBillingLastName.setText(query.value(13))
			self.ui.txtBillingEmail.setText(query.value(14))
			self.ui.txtsBillingPhone.setText(query.value(15))
			self.ui.txtBillingAddress1.setText(query.value(16))
			self.ui.txtBillingAddress2.setText(query.value(17))
			self.ui.txtBillingCity.setText(query.value(18))
			self.ui.txtBillingZipcode.setText(query.value(19))

			index = self.ui.cbBillingState.findText(query.value(20), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbBillingState.setCurrentIndex(index)

			index = self.ui.cbBillingCountry.findText(query.value(21), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbBillingCountry.setCurrentIndex(index)

			index = self.ui.cbCardType.findText(query.value(22), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbCardType.setCurrentIndex(index)

			self.ui.txtCardName.setText(query.value(23))
			self.ui.txtCardNumber.setText(query.value(24))
			self.ui.txtCvv.setText(query.value(25))

			index = self.ui.cbExpiryMonth.findText(query.value(26), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbExpiryMonth.setCurrentIndex(index)

			index = self.ui.cbExpiryYear.findText(query.value(27), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbExpiryYear.setCurrentIndex(index)

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
		query.addBindValue(self.ui.txtProfileName.text())

		query.addBindValue(self.ui.txtShippingFirstName.text())
		query.addBindValue(self.ui.txtShippingLastName.text())
		query.addBindValue(self.ui.txtShippingEmail.text())
		query.addBindValue(self.ui.txtsShippingPhone.text())
		query.addBindValue(self.ui.txtShippingAddress1.text())
		query.addBindValue(self.ui.txtShippingAddress2.text())
		query.addBindValue(self.ui.txtShippingCity.text())
		query.addBindValue(self.ui.txtShippingZipcode.text())
		query.addBindValue(self.ui.cbShippingState.currentText())
		query.addBindValue(self.ui.cbShippingCountry.currentText())

		query.addBindValue(self.ui.txtBillingFirstName.text())
		query.addBindValue(self.ui.txtBillingLastName.text())
		query.addBindValue(self.ui.txtBillingEmail.text())
		query.addBindValue(self.ui.txtsBillingPhone.text())
		query.addBindValue(self.ui.txtBillingAddress1.text())
		query.addBindValue(self.ui.txtBillingAddress2.text())
		query.addBindValue(self.ui.txtBillingCity.text())
		query.addBindValue(self.ui.txtBillingZipcode.text())
		query.addBindValue(self.ui.cbBillingState.currentText())
		query.addBindValue(self.ui.cbBillingCountry.currentText())

		query.addBindValue(self.ui.cbCardType.currentText())
		query.addBindValue(self.ui.txtCardName.text())
		query.addBindValue(self.ui.txtCardNumber.text())
		query.addBindValue(self.ui.txtCvv.text())
		query.addBindValue(self.ui.cbExpiryMonth.currentText())
		query.addBindValue(self.ui.cbExpiryYear.currentText())
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
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
		query.addBindValue(self.ui.txtProfileName.text())

		query.addBindValue(self.ui.txtShippingFirstName.text())
		query.addBindValue(self.ui.txtShippingLastName.text())
		query.addBindValue(self.ui.txtShippingEmail.text())
		query.addBindValue(self.ui.txtsShippingPhone.text())
		query.addBindValue(self.ui.txtShippingAddress1.text())
		query.addBindValue(self.ui.txtShippingAddress2.text())
		query.addBindValue(self.ui.txtShippingCity.text())
		query.addBindValue(self.ui.txtShippingZipcode.text())
		query.addBindValue(self.ui.cbShippingState.currentText())
		query.addBindValue(self.ui.cbShippingCountry.currentText())

		query.addBindValue(self.ui.txtBillingFirstName.text())
		query.addBindValue(self.ui.txtBillingLastName.text())
		query.addBindValue(self.ui.txtBillingEmail.text())
		query.addBindValue(self.ui.txtsBillingPhone.text())
		query.addBindValue(self.ui.txtBillingAddress1.text())
		query.addBindValue(self.ui.txtBillingAddress2.text())
		query.addBindValue(self.ui.txtBillingCity.text())
		query.addBindValue(self.ui.txtBillingZipcode.text())
		query.addBindValue(self.ui.cbBillingState.currentText())
		query.addBindValue(self.ui.cbBillingCountry.currentText())

		query.addBindValue(self.ui.cbCardType.currentText())
		query.addBindValue(self.ui.txtCardName.text())
		query.addBindValue(self.ui.txtCardNumber.text())
		query.addBindValue(self.ui.txtCvv.text())
		query.addBindValue(self.ui.cbExpiryMonth.currentText())
		query.addBindValue(self.ui.cbExpiryYear.currentText())

		query.addBindValue(str(self.profile_id))
		if not query.exec():
			QMessageBox.critical(self, "Rabbit - Error!", 'Database Error: %s' % query.lastError().text(),)
		else:
			self.close()

	def cbSameAsShippingClicked(self,state):
		if state == QtCore.Qt.Checked:
			self.ui.txtBillingFirstName.setText(self.ui.txtShippingFirstName.text())
			self.ui.txtBillingLastName.setText(self.ui.txtShippingLastName.text())
			self.ui.txtBillingEmail.setText(self.ui.txtShippingEmail.text())
			self.ui.txtsBillingPhone.setText(self.ui.txtsShippingPhone.text())
			self.ui.txtBillingAddress1.setText(self.ui.txtShippingAddress1.text())
			self.ui.txtBillingAddress2.setText(self.ui.txtShippingAddress2.text())
			self.ui.txtBillingCity.setText(self.ui.txtShippingCity.text())

			index = self.ui.cbBillingState.findText(self.ui.cbShippingState.currentText(), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbBillingState.setCurrentIndex(index)

			self.ui.txtBillingZipcode.setText(self.ui.txtShippingZipcode.text())

			index = self.ui.cbBillingCountry.findText(self.ui.cbShippingCountry.currentText(), QtCore.Qt.MatchFixedString)
			if index >= 0:
				self.ui.cbBillingCountry.setCurrentIndex(index)
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import *
import sys
import os

class ProfileWindown(QtWidgets.QMainWindow):
	def __init__(self):
		super(ProfileWindown, self).__init__()
		uic.loadUi(os.path.join("ui", "profile.ui"), self)
		
		# create connection for button
		self.btnAdd.clicked.connect(self.on_btnAdd_clicked)
		self.btnEdit.clicked.connect(self.on_btnEdit_clicked)
		self.btnDelete.clicked.connect(self.on_btnDelete_clicked)
		self.btnDeleteAll.clicked.connect(self.on_btnDeleteAll_clicked)

		# create table header
		model = QtGui.QStandardItemModel()
		model.setHorizontalHeaderLabels(['ID', 'NAME', 'EMAIL', 'PHONE', 'CARD TYPE'])
		self.tbProfile.setModel(model)

	def on_btnAdd_clicked(self):
		self.createProfileFrm = CreateProfileWindown()
		self.createProfileFrm.show()

	def on_btnEdit_clicked(self):
		self.editProfileFrm = EditProfileWindown()
		self.editProfileFrm.show()

	def on_btnDelete_clicked(self):
		print("Delete button press")

	def on_btnDeleteAll_clicked(self):
		print("Delete All button press")


class CreateProfileWindown(QtWidgets.QMainWindow):
	def __init__(self):
		super(CreateProfileWindown, self).__init__()
		uic.loadUi(os.path.join("ui", "create_profile.ui"), self)

		# create connection for button
		self.btnCreate.clicked.connect(self.on_btnCreate_clicked)
		self.btnCancel.clicked.connect(self.on_btnCancel_clicked)

	def on_btnCreate_clicked(self):
		print("Create button press")

	def on_btnCancel_clicked(self):
		self.close()


class EditProfileWindown(QtWidgets.QMainWindow):
	def __init__(self):
		super(EditProfileWindown, self).__init__()
		uic.loadUi(os.path.join("ui", "edit_profile.ui"), self)

		# create connection for button
		self.btnUpdate.clicked.connect(self.on_btnUpdate_clicked)
		self.btnCancel.clicked.connect(self.on_btnCancel_clicked)

	def on_btnUpdate_clicked(self):
		print("Update button press")

	def on_btnCancel_clicked(self):
		self.close()
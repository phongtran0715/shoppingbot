from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
import sys
import os


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		uic.loadUi(os.path.join("ui", "supreme.ui"), self)

		self.profileManager = ProfileWindow()
		
		# set table header
		# self.tbListTask.setHorizontalHeaderLabels(['ID', 'ITEM', 'CATEGORY', 'SIZE', 'COLOUR', 'BILLING PROFILE', 'STATUS'])

		# set button actions
		self.btnStartAll.clicked.connect(self.startAllButtonPress)
		self.btnCreateTask.clicked.connect(self.btnCreateTaskPress)
		self.actionProfile_Manager.triggered.connect(self.actionProfileManagetPress)
		self.show()

	def startAllButtonPress(self):
		print("start All button press");

	def btnCreateTaskPress(self):
		print("create new task")

	def actionProfileManagetPress(self):
		print("Profile manager press")
		self.profileManager.show()


class ProfileWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(ProfileWindow, self).__init__(parent)
		uic.loadUi(os.path.join("ui", "profile.ui"))


class EditProfileWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(EditProfileWindow, self).__init__()
		uic.loadUi(os.path.join("ui", "edit_profile.ui"))

class AddNewProfileWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(AddNewProfileWindow, self).__init__()
		uic.loadUi(os.path.join("ui", "add_new_profile.ui"))


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
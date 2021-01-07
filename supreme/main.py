from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import *
from profile_manager import ProfileWindown
import sys
import os


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		uic.loadUi(os.path.join("ui", "supreme.ui"), self)

		# create connection for button
		self.actionProfile_Manager.triggered.connect(self.on_actionProfileManaget_triggered)

		# create table header
		model = QtGui.QStandardItemModel()
		model.setHorizontalHeaderLabels(['ID', 'ITEM', 'CATEGORY', 'COLOUR', 'PROFILE', 'STATUS', 'ACTION'])
		self.tbListTask.setModel(model)

	def on_actionProfileManaget_triggered(self):
		self.profileFrm = ProfileWindown()
		self.profileFrm.show()


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
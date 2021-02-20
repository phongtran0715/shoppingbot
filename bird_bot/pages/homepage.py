from theming.styles import globalStyles
from PyQt5 import QtCore, QtGui, QtWidgets
from sites.walmart import Walmart
from sites.bestbuy import BestBuy
from sites.target import Target
from sites.gamestop import GameStop
from pages.createdialog import CreateDialog
from pages.new_task_dialog import NewTask
from pages.pollbrowser import PollBrowserDialog
from utils import get_profile, get_proxy, BirdLogger, return_data, write_data
from utils.selenium_utils import open_browser
import urllib.request,sys,platform
import settings
from pages.task_tab import TaskTab
from model.task_model import TaskModel


def no_abort(a, b, c):
	sys.__excepthook__(a, b, c)
sys.excepthook = no_abort
logger = BirdLogger()


class HomePage(QtWidgets.QWidget):
	def __init__(self,parent=None):
		super(HomePage, self).__init__(parent)
		self.setupUi(self)
		self.load_tasks()

	def setupUi(self, homepage):
		global tasks
		self.tasks = []
		tasks = self.tasks
		self.homepage = homepage
		self.homepage.setAttribute(QtCore.Qt.WA_StyledBackground, True)
		self.homepage.setGeometry(QtCore.QRect(60, 0, 1041, 601))

		self.tasks_card = QtWidgets.QWidget(self.homepage)
		self.tasks_card.setGeometry(QtCore.QRect(30, 110, 991, 461))
		self.tasks_card.setStyleSheet("background-color: {};border-radius: 20px;border: 1px solid #2e2d2d;".format(globalStyles["backgroundLight"]))

		self.scrollArea = QtWidgets.QScrollArea(self.tasks_card)
		self.scrollArea.setGeometry(QtCore.QRect(20, 30, 951, 421))
		self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.scrollArea.setStyleSheet("border:none;")
		self.scrollArea.setWidgetResizable(True)
		self.scrollAreaWidgetContents = QtWidgets.QWidget()
		self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 951, 421))
		self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
		self.verticalLayout.setContentsMargins(0, -1, 0, -1)
		self.verticalLayout.setSpacing(2)
		spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout.addItem(spacerItem)
		self.scrollArea.setWidget(self.scrollAreaWidgetContents)
		self.image_table_header = QtWidgets.QLabel(self.tasks_card)
		self.image_table_header.setGeometry(QtCore.QRect(40, 7, 51, 31))
		self.image_table_header.setText("Image")
		font = QtGui.QFont()
		font.setFamily("Arial")
		font.setPointSize(15) if platform.system() == "Darwin" else font.setPointSize(15*.75)
		font.setBold(False)
		font.setWeight(50)
		self.image_table_header.setFont(font)
		self.image_table_header.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.product_table_header = QtWidgets.QLabel(self.tasks_card)
		self.product_table_header.setGeometry(QtCore.QRect(240, 7, 61, 31))
		self.product_table_header.setFont(font)
		self.product_table_header.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.product_table_header.setText("Product")
		self.profile_table_header = QtWidgets.QLabel(self.tasks_card)
		self.profile_table_header.setGeometry(QtCore.QRect(590, 7, 61, 31))
		self.profile_table_header.setFont(font)
		self.profile_table_header.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.profile_table_header.setText("Account")
		self.status_table_header = QtWidgets.QLabel(self.tasks_card)
		self.status_table_header.setGeometry(QtCore.QRect(650, 7, 61, 31))
		self.status_table_header.setFont(font)
		self.status_table_header.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.status_table_header.setText("Status")
		self.actions_table_header = QtWidgets.QLabel(self.tasks_card)
		self.actions_table_header.setGeometry(QtCore.QRect(890, 7, 61, 31))
		self.actions_table_header.setFont(font)
		self.actions_table_header.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.actions_table_header.setText("Actions")
		self.site_table_header = QtWidgets.QLabel(self.tasks_card)
		self.site_table_header.setGeometry(QtCore.QRect(160, 7, 61, 31))
		self.site_table_header.setFont(font)
		self.site_table_header.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.site_table_header.setText("Site")
		self.id_header = QtWidgets.QLabel(self.tasks_card)
		self.id_header.setGeometry(QtCore.QRect(110, 7, 31, 31))
		self.id_header.setFont(font)
		self.id_header.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.id_header.setText("ID")
		self.tasks_header = QtWidgets.QLabel(self.homepage)
		self.tasks_header.setGeometry(QtCore.QRect(30, 10, 61, 31))
		self.tasks_header.setText("Tasks")
		font = QtGui.QFont()
		font.setFamily("Arial")
		font.setPointSize(22) if platform.system() == "Darwin" else font.setPointSize(22*.75)
		font.setBold(False)
		font.setWeight(50)
		self.tasks_header.setFont(font)
		self.tasks_header.setStyleSheet("color: rgb(234, 239, 239);")
		self.checkouts_card = QtWidgets.QWidget(self.homepage)
		self.checkouts_card.setGeometry(QtCore.QRect(440, 45, 171, 51))
		self.checkouts_card.setStyleSheet("background-color: {};border-radius: 10px;border: 1px solid #2e2d2d;".format(globalStyles["backgroundLight"]))
		self.checkouts_label = QtWidgets.QLabel(self.checkouts_card)
		self.checkouts_label.setGeometry(QtCore.QRect(78, 10, 81, 31))
		font = QtGui.QFont()
		font.setFamily("Arial")
		font.setPointSize(16) if platform.system() == "Darwin" else font.setPointSize(16*.75)
		font.setBold(False)
		font.setWeight(50)
		self.checkouts_label.setFont(font)
		self.checkouts_label.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.checkouts_label.setText("Checkouts")
		self.checkouts_icon = QtWidgets.QLabel(self.checkouts_card)
		self.checkouts_icon.setGeometry(QtCore.QRect(10, 10, 31, 31))
		self.checkouts_icon.setStyleSheet("border: none;")
		self.checkouts_icon.setText("")
		self.checkouts_icon.setPixmap(QtGui.QPixmap("images/success.png"))
		self.checkouts_icon.setScaledContents(True)
		
		global checkouts_count
		self.checkouts_count = QtWidgets.QLabel(self.checkouts_card)
		checkouts_count = self.checkouts_count
		self.checkouts_count.setGeometry(QtCore.QRect(43, 10, 31, 31))
		self.checkouts_count.setFont(font)
		self.checkouts_count.setStyleSheet("color: #34C693;border: none;")
		self.checkouts_count.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.checkouts_count.setText("0")
		self.tasks_total_card = QtWidgets.QWidget(self.homepage)
		self.tasks_total_card.setGeometry(QtCore.QRect(30, 45, 181, 51))
		self.tasks_total_card.setStyleSheet("background-color: {};border-radius: 10px;border: 1px solid #2e2d2d;".format(globalStyles["backgroundLight"]))
		self.tasks_total_label = QtWidgets.QLabel(self.tasks_total_card)
		self.tasks_total_label.setGeometry(QtCore.QRect(80, 10, 91, 31))
		self.tasks_total_label.setFont(font)
		self.tasks_total_label.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.tasks_total_label.setText("Total Tasks")
		self.tasks_total_icon = QtWidgets.QLabel(self.tasks_total_card)
		self.tasks_total_icon.setGeometry(QtCore.QRect(10, 10, 31, 31))
		self.tasks_total_icon.setStyleSheet("border: none;")
		self.tasks_total_icon.setText("")
		self.tasks_total_icon.setPixmap(QtGui.QPixmap("images/tasks.png"))
		self.tasks_total_icon.setScaledContents(True)
		
		global tasks_total_count
		self.tasks_total_count = QtWidgets.QLabel(self.tasks_total_card)
		tasks_total_count = self.tasks_total_count
		self.tasks_total_count.setGeometry(QtCore.QRect(43, 10, 31, 31))
		self.tasks_total_count.setFont(font)
		self.tasks_total_count.setStyleSheet("color: {};border: none;".format(globalStyles['primary']))
		self.tasks_total_count.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.tasks_total_count.setText("0")
		self.carted_card = QtWidgets.QWidget(self.homepage)
		self.carted_card.setGeometry(QtCore.QRect(240, 45, 171, 51))
		self.carted_card.setStyleSheet("background-color: {};border-radius: 10px;border: 1px solid #2e2d2d;".format(globalStyles["backgroundLight"]))
		self.carted_label = QtWidgets.QLabel(self.carted_card)
		self.carted_label.setGeometry(QtCore.QRect(80, 10, 90, 31))
		self.carted_label.setFont(font)
		self.carted_label.setStyleSheet("color: rgb(234, 239, 239);border: none;")
		self.carted_label.setText("Total Carts")
		self.carted_icon = QtWidgets.QLabel(self.carted_card)
		self.carted_icon.setGeometry(QtCore.QRect(10, 10, 31, 31))
		self.carted_icon.setStyleSheet("border: none;")
		self.carted_icon.setText("")
		self.carted_icon.setPixmap(QtGui.QPixmap("images/cart.png"))
		self.carted_icon.setScaledContents(True)
		
		global carted_count
		self.carted_count = QtWidgets.QLabel(self.carted_card)
		carted_count = self.carted_count
		self.carted_count.setGeometry(QtCore.QRect(43, 10, 31, 31))
		self.carted_count.setFont(font)
		self.carted_count.setStyleSheet("color: {};border: none;".format(globalStyles["cartedColor"]))
		self.carted_count.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.carted_count.setText("0")
		self.buttons_card = QtWidgets.QWidget(self.homepage)
		self.buttons_card.setGeometry(QtCore.QRect(640, 45, 381, 51))
		self.buttons_card.setStyleSheet("background-color: {};border-radius: 10px;border: 1px solid #2e2d2d;".format(globalStyles["backgroundLight"]))
		
		self.startall_btn = QtWidgets.QPushButton(self.buttons_card)
		self.startall_btn.setGeometry(QtCore.QRect(103, 10, 86, 32))
		font = QtGui.QFont()
		font.setFamily("Arial")
		self.startall_btn.setFont(font)
		self.startall_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.startall_btn.setStyleSheet("color: #FFFFFF;background-color: {};border: none;".format(globalStyles["primary"]))
		self.startall_btn.setText("Start All")
		self.startall_btn.clicked.connect(self.start_all_tasks)
		
		self.stopall_btn = QtWidgets.QPushButton(self.buttons_card)
		self.stopall_btn.setGeometry(QtCore.QRect(197, 10, 81, 32))
		self.stopall_btn.setFont(font)
		self.stopall_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.stopall_btn.setStyleSheet("color: #FFFFFF;background-color: {};border: none;".format(globalStyles["primary"]))
		self.stopall_btn.setText("Stop All")
		self.stopall_btn.clicked.connect(self.stop_all_tasks)
		
		self.deleteall_btn = QtWidgets.QPushButton(self.buttons_card)
		self.deleteall_btn.setGeometry(QtCore.QRect(285, 10, 86, 32))
		self.deleteall_btn.setFont(font)
		self.deleteall_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.deleteall_btn.setStyleSheet("color: #FFFFFF;background-color: {};border: none;".format(globalStyles["primary"]))
		self.deleteall_btn.setText("Delete All")
		self.deleteall_btn.clicked.connect(self.delete_all_tasks)
		
		self.newtask_btn = QtWidgets.QPushButton(self.buttons_card)
		self.newtask_btn.setGeometry(QtCore.QRect(10, 10, 86, 32))
		self.newtask_btn.setFont(font)
		self.newtask_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.newtask_btn.setStyleSheet("color: #FFFFFF;background-color: {};border: none;".format(globalStyles["primary"]))
		self.newtask_btn.setText("New Task")
		self.newtask_btn.clicked.connect(self.btn_new_task_clicked)
		QtCore.QMetaObject.connectSlotsByName(homepage)

	def load_tasks(self):
		tasks_data = return_data("./data/tasks.json")
		new_tasks_data = []
		task_id = 1
		for task in tasks_data:
			task['task_id'] = str(task_id)
			self.add_tab(task)
			new_tasks_data.append(task)
		write_data("./data/tasks.json",new_tasks_data)

	def add_tab(self, task):
		tab = TaskTab(str(task["task_id"]), task["site"],task["product"],task["monitor_proxy"],
				task["monitor_delay"], task["error_delay"], task["max_price"],task["max_quantity"],
				task["account"], self.stop_all_tasks,self.scrollAreaWidgetContents, self)
		self.verticalLayout.takeAt(self.verticalLayout.count()-1)
		self.verticalLayout.addWidget(tab)
		spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.verticalLayout.addItem(spacerItem)

		tasks_total_count.setText(str(int(tasks_total_count.text()) + 1))

	def btn_new_task_clicked(self):
		self.new_task_frm = NewTask(self)
		self.new_task_frm.show()
		if self.new_task_frm.exec_() == QtWidgets.QDialog.Accepted:
			self.new_task_frm.save_task()

	def set_settings_data(self,settings_data):
		global settings
		settings = settings_data

	def start_all_tasks(self):
		for task in self.tasks:
			try:
				task.start(None)
			except:
				pass
	def stop_all_tasks(self):
		for task in self.tasks:
			try:
				task.stop(None)
			except:
				pass

	def delete_all_tasks(self):
		for task in self.tasks:
			try:
				task.delete(None)
			except:
				pass

class TaskThread(QtCore.QThread):
	status_signal = QtCore.pyqtSignal("PyQt_PyObject")
	image_signal = QtCore.pyqtSignal("PyQt_PyObject")
	wait_poll_signal = QtCore.pyqtSignal()
	def __init__(self):
		QtCore.QThread.__init__(self)

	def set_data(self,task_id,site,product,profile,monitor_proxies,shopping_proxies,monitor_delay,error_delay,max_price, max_quantity):
		self.task_id,self.site,self.product,self.profile,self.monitor_proxies,self.shopping_proxies,self.monitor_delay,self.error_delay,self.max_price,self.max_quantity = task_id,site,product,profile,monitor_proxies,shopping_proxies,monitor_delay,error_delay,max_price,max_quantity

	def run(self):
		profile = get_profile(self.profile)
		if profile is None:
			self.status_signal.emit({"msg": "Invalid profile", "status": "error"})
			return
		if self.site == "Walmart":
			Walmart(self.task_id,self.status_signal, self.image_signal,  self.wait_poll_signal, self.wait_condition, self.product, profile, self.monitor_proxies, self.shopping_proxies, self.monitor_delay, self.error_delay, self.max_price, self.max_quantity)
		elif self.site == "Bestbuy":
			BestBuy(self.status_signal, self.image_signal, self.product, profile, self.monitor_proxies,self.shopping_proxies, self.monitor_delay, self.error_delay) #TODO: Readd Discord Webhook
		elif self.site == "Target":
			Target(self.task_id, self.status_signal, self.image_signal, self.product, profile, self.monitor_proxies,self.shopping_proxies, self.monitor_delay, self.error_delay)
		elif self.site == "GameStop":
			GameStop(self.task_id, self.status_signal, self.image_signal, self.product, profile, self.monitor_proxies, self.shopping_proxies, self.monitor_delay, self.error_delay, self.max_price, self.max_quantity)

	def stop(self):
		self.terminate()

class ImageThread(QtCore.QThread):
	finished_signal = QtCore.pyqtSignal("PyQt_PyObject")
	def __init__(self,image_url):
		self.image_url = image_url
		QtCore.QThread.__init__(self)

	def run(self):
		data = urllib.request.urlopen(self.image_url).read()
		pixmap = QtGui.QPixmap()
		pixmap.loadFromData(data)
		self.finished_signal.emit(pixmap)

class BrowserThread(QtCore.QThread):
	def __init__(self):
		QtCore.QThread.__init__(self)

	def set_data(self,url,cookies):
		self.url,self.cookies = url,cookies
	def run(self):
		open_browser(self.url,self.cookies)


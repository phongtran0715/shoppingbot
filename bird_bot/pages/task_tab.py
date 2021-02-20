from theming.styles import globalStyles
from PyQt5 import QtCore, QtGui, QtWidgets
from sites.walmart import Walmart
from sites.bestbuy import BestBuy
from sites.target import Target
from sites.gamestop import GameStop
from pages.createdialog import CreateDialog
from pages.pollbrowser import PollBrowserDialog
from utils import get_profile, get_proxy, BirdLogger, return_data, write_data
from utils.selenium_utils import open_browser
import urllib.request,sys,platform
import settings


class TaskTab(QtWidgets.QWidget):
    def __init__(self,task_id, site,product,monitor_proxies,monitor_delay,error_delay,max_price,max_quantity,account, stop_all, scroll_content, parent=None):
        super(TaskTab, self).__init__(parent)
        self.task_id = task_id;
        self.site = site
        self.product = product
        self.monitor_proxies = monitor_proxies
        self.monitor_delay = monitor_delay
        self.error_delay =error_delay
        self.max_price = max_price
        self.max_quantity = max_quantity
        self.stop_all = stop_all
        self.account = account
        self.parent = parent
        self.setupUi(self)

    def setupUi(self,TaskTab):
        self.running = False

        self.TaskTab = TaskTab
        self.TaskTab.setMinimumSize(QtCore.QSize(0, 50))
        self.TaskTab.setMaximumSize(QtCore.QSize(16777215, 50))
        self.TaskTab.setStyleSheet("border-radius: none;")
        self.product_label = QtWidgets.QLabel(self.TaskTab)
        self.product_label.setGeometry(QtCore.QRect(222, 10, 331, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(13) if platform.system() == "Darwin" else font.setPointSize(13*.75)
        font.setBold(False)
        font.setWeight(50)
        self.product_label.setFont(font)
        self.product_label.setStyleSheet("color: rgb(234, 239, 239);")
        self.profile_label = QtWidgets.QLabel(self.TaskTab)
        self.profile_label.setGeometry(QtCore.QRect(571, 10, 51, 31))
        self.profile_label.setFont(font)
        self.profile_label.setStyleSheet("color: rgb(234, 239, 239);")
        
        self.status_label = QtWidgets.QLabel(self.TaskTab)
        self.status_label.setGeometry(QtCore.QRect(632, 10, 231, 31))
        self.status_label.setFont(font)
        self.status_label.setStyleSheet("color: rgb(234, 239, 239);")
        
        self.browser_label = QtWidgets.QLabel(self.TaskTab)
        self.browser_label.setGeometry(QtCore.QRect(632, 10, 231, 31))
        self.browser_label.setFont(font)
        self.browser_label.setStyleSheet("color: rgb(163, 149, 255);")
        self.browser_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.browser_label.mousePressEvent = self.open_browser
        self.browser_label.hide()
        
        self.start_btn = QtWidgets.QLabel(self.TaskTab)
        self.start_btn.setGeometry(QtCore.QRect(870, 15, 16, 16))
        self.start_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.start_btn.setPixmap(QtGui.QPixmap("images/play.png"))
        self.start_btn.setScaledContents(True)
        self.start_btn.mousePressEvent = self.start
        
        self.stop_btn = QtWidgets.QLabel(self.TaskTab)
        self.stop_btn.setGeometry(QtCore.QRect(870, 15, 16, 16))
        self.stop_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.stop_btn.setPixmap(QtGui.QPixmap("images/stop.png"))
        self.stop_btn.setScaledContents(True)
        self.stop_btn.mousePressEvent = self.stop
        
        self.delete_btn = QtWidgets.QLabel(self.TaskTab)
        self.delete_btn.setGeometry(QtCore.QRect(920, 15, 16, 16))
        self.delete_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.delete_btn.setPixmap(QtGui.QPixmap("images/trash.png"))
        self.delete_btn.setScaledContents(True)
        self.delete_btn.mousePressEvent = self.delete
        
        self.edit_btn = QtWidgets.QLabel(self.TaskTab)
        self.edit_btn.setGeometry(QtCore.QRect(895, 15, 16, 16))
        self.edit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.edit_btn.setPixmap(QtGui.QPixmap("images/edit.png"))
        self.edit_btn.setScaledContents(True)
        self.edit_btn.mousePressEvent = self.edit
        
        self.image = QtWidgets.QLabel(self.TaskTab)
        self.image.setGeometry(QtCore.QRect(20, 0, 50, 50))
        self.image.setPixmap(QtGui.QPixmap("images/no_image.png"))
        self.image.setScaledContents(True)

        self.site_label = QtWidgets.QLabel(self.TaskTab)
        self.site_label.setGeometry(QtCore.QRect(140, 10, 61, 31))
        self.site_label.setFont(font)
        self.site_label.setStyleSheet("color: rgb(234, 239, 239);")

        self.id_label = QtWidgets.QLabel(self.TaskTab)
        self.id_label.setGeometry(QtCore.QRect(90, 10, 31, 31))
        self.id_label.setFont(font)
        self.id_label.setStyleSheet("color: rgb(234, 239, 239);")
        
        self.stop_btn.raise_()
        self.product_label.raise_()
        self.profile_label.raise_()
        self.browser_label.raise_()
        self.start_btn.raise_()
        self.delete_btn.raise_()
        self.image.raise_()
        self.site_label.raise_()

        self.monitor_delay_label = QtWidgets.QLabel(self.TaskTab)
        self.monitor_delay_label.hide()
        self.error_delay_label = QtWidgets.QLabel(self.TaskTab)
        self.error_delay_label.hide()
        self.max_price_label = QtWidgets.QLabel(self.TaskTab)
        self.max_price_label.hide()
        self.max_quantity_label = QtWidgets.QLabel(self.TaskTab)
        self.max_quantity_label.hide()
        self.monitor_proxies_label = QtWidgets.QLabel(self.TaskTab)
        self.monitor_proxies_label.hide()
        self.shopping_proxies_label = QtWidgets.QLabel(self.TaskTab)
        self.shopping_proxies_label.hide()
        self.load_labels()

    def load_labels(self):
        self.id_label.setText(self.task_id)
        self.product_label.setText(self.product)
        self.profile_label.setText(self.account)
        self.monitor_proxies_label.setText(self.monitor_proxies)
        self.status_label.setText("Idle")
        self.browser_label.setText("Click To Open Browser")
        self.site_label.setText(self.site)
        self.monitor_delay_label.setText(self.monitor_delay)
        self.error_delay_label.setText(self.error_delay)
        self.max_price_label.setText(self.max_price)
        self.max_quantity_label.setText(self.max_quantity)

    def update_status(self,msg):
        self.status_label.setText(msg["msg"])
        if msg["msg"] == "Browser Ready":
            self.browser_url,self.browser_cookies = msg["url"],msg["cookies"]
            self.running = False
            self.start_btn.raise_()
            self.browser_label.show()
            logger.alt(self.task_id,msg["msg"])
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(1000, loop.quit)
            loop.exec_()
            self.task.stop()
            return
        if msg["status"] == "idle":
            self.status_label.setStyleSheet("color: rgb(255, 255, 255);")
            logger.normal(self.task_id,msg["msg"])
        elif msg["status"] == "normal":
            self.status_label.setStyleSheet("color: rgb(163, 149, 255);")
            logger.normal(self.task_id,msg["msg"])
        elif msg["status"] == "alt":
            self.status_label.setStyleSheet("color: rgb(242, 166, 137);")
            logger.alt(self.task_id,msg["msg"])
        elif msg["status"] == "error":
            self.status_label.setStyleSheet("color: rgb(252, 81, 81);")
            logger.error(self.task_id,msg["msg"])
        elif msg["status"] == "success":
            self.status_label.setStyleSheet("color: rgb(52, 198, 147);")
            logger.success(self.task_id,msg["msg"])
            self.running = False
            self.start_btn.raise_()
            if settings.buy_one:
                self.stop_all()
            checkouts_count.setText(str(int(checkouts_count.text())+1))
        elif msg["status"] == "carted":
            self.status_label.setStyleSheet("color: rgb(163, 149, 255);")
            logger.alt(self.task_id,msg["msg"])
            carted_count.setText(str(int(carted_count.text())+1))
    
    def wait_browser_poll(self):
        # Initiate dialog and block until dismissed
        poll_browser_dialog = PollBrowserDialog(self.parent())
        poll_browser_dialog.exec()

        # set wait condition
        self.task.wait_condition.wakeAll()

        pass

    def update_image(self,image_url):
        self.image_thread = ImageThread(image_url)
        self.image_thread.finished_signal.connect(self.set_image)
        self.image_thread.start()

    def set_image(self,pixmap):
        self.image.setPixmap(pixmap)

    def start(self,event):
        if not self.running:
            self.browser_label.hide()
            self.task = TaskThread()
            self.task.status_signal.connect(self.update_status)
            self.task.image_signal.connect(self.update_image)
            self.task.wait_condition = QtCore.QWaitCondition()
            
            # Special case for Walmart, not sure if should disambiguate
            # allowing other stores to use functionality
            if self.site == "Walmart":
                self.task.wait_poll_signal.connect(self.wait_browser_poll)

            self.task.set_data(
                self.task_id,
                self.site_label.text(),
                self.product_label.text(),
                self.monitor_proxies_label.text(),
                self.monitor_delay_label.text(),
                self.error_delay_label.text(),
                self.max_price_label.text(),
                self.max_quantity_label.text(),
                self.profile_label.text()
            )
            self.task.start()
            self.running = True
            self.stop_btn.raise_()

    def stop(self,event):
        self.task.stop()
        self.running = False
        self.update_status({"msg":"Stopped","status":"idle"})
        self.start_btn.raise_()

    def edit(self,event):
        pass
        # self.edit_dialog = NewTask()
        # # self.edit_dialog.load_data(self)
        # self.edit_dialog.show()
        # if self.edit_dialog.exec_() == QtWidgets.QDialog.Accepted:
        #     pass
        #     # TODO: update task

    def update_task(self):
        self.site=self.edit_dialog.site_box.currentText()
        self.product=self.edit_dialog.input_edit.text()
        self.account=self.edit_dialog.profile_box.currentText()
        self.monitor_proxies=self.edit_dialog.monitor_proxies_box.currentText()
        self.monitor_delay=self.edit_dialog.monitor_edit.text()
        self.error_delay = self.edit_dialog.error_edit.text()
        self.max_price = self.edit_dialog.price_edit.text()
        self.max_quantity = self.edit_dialog.quantity_edit.text()
        self.load_labels()
        self.delete_json()
        tasks_data = return_data("./data/tasks.json")
        task_data = {"task_id": self.task_id, "site": self.site, "product": self.product,
                     "monitor_proxies": self.monitor_proxies, "monitor_delay": self.monitor_delay,
                     "error_delay": self.error_delay, "max_price": self.max_price,
                     "max_quantity": self.max_quantity, "account": self.account}
        tasks_data.append(task_data)
        write_data("./data/tasks.json",tasks_data)
        self.edit_dialog.deleteLater()

    def delete_json(self):
        tasks_data = return_data("./data/tasks.json")
        for task in tasks_data:
            if task["task_id"] == self.task_id:
                tasks_data.remove(task)
                break
        write_data("./data/tasks.json", tasks_data)

    def delete(self,event):
        self.parent.tasks_total_count.setText(str(int(self.parent.tasks_total_count.text()) - 1))
        self.delete_json()
        self.TaskTab.deleteLater()

    def open_browser(self,event):
        self.browser_thread = BrowserThread()
        self.browser_thread.set_data(
            self.browser_url,
            self.browser_cookies
        )
        self.browser_thread.start()
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './new_account.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(340, 271)
        font = QtGui.QFont()
        font.setPointSize(11)
        Dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./../../images/rabbit.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.cbSite = QtWidgets.QComboBox(Dialog)
        self.cbSite.setEditable(False)
        self.cbSite.setObjectName("cbSite")
        self.cbSite.addItem("")
        self.cbSite.addItem("")
        self.cbSite.addItem("")
        self.cbSite.addItem("")
        self.gridLayout.addWidget(self.cbSite, 0, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setIndent(5)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setIndent(5)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 4, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 9, 2, 1, 2)
        self.txtPassword = QtWidgets.QLineEdit(Dialog)
        self.txtPassword.setObjectName("txtPassword")
        self.gridLayout.addWidget(self.txtPassword, 3, 3, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setIndent(5)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.cbProxy = QtWidgets.QComboBox(Dialog)
        self.cbProxy.setObjectName("cbProxy")
        self.cbProxy.addItem("")
        self.cbProxy.setItemText(0, "")
        self.gridLayout.addWidget(self.cbProxy, 4, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setIndent(5)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 1, 1, 2)
        self.txtName = QtWidgets.QLineEdit(Dialog)
        self.txtName.setObjectName("txtName")
        self.gridLayout.addWidget(self.txtName, 1, 3, 1, 1)
        self.txtUsername = QtWidgets.QLineEdit(Dialog)
        self.txtUsername.setObjectName("txtUsername")
        self.gridLayout.addWidget(self.txtUsername, 2, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setIndent(5)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 8, 1, 1, 3)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setIndent(5)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 7, 1, 1, 1)
        self.cbProfile = QtWidgets.QComboBox(Dialog)
        self.cbProfile.setObjectName("cbProfile")
        self.cbProfile.addItem("")
        self.cbProfile.setItemText(0, "")
        self.gridLayout.addWidget(self.cbProfile, 7, 3, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.txtName, self.txtUsername)
        Dialog.setTabOrder(self.txtUsername, self.txtPassword)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add new account"))
        self.cbSite.setItemText(0, _translate("Dialog", "GameStop"))
        self.cbSite.setItemText(1, _translate("Dialog", "Walmart"))
        self.cbSite.setItemText(2, _translate("Dialog", "Target"))
        self.cbSite.setItemText(3, _translate("Dialog", "Bestbuy"))
        self.label_3.setText(_translate("Dialog", "Password"))
        self.label_6.setText(_translate("Dialog", "Proxy"))
        self.txtPassword.setToolTip(_translate("Dialog", "<html><head/><body><p>Main address</p></body></html>"))
        self.label.setText(_translate("Dialog", "Site"))
        self.label_4.setText(_translate("Dialog", "Use Name"))
        self.txtName.setToolTip(_translate("Dialog", "<html><head/><body><p>Email address</p></body></html>"))
        self.txtUsername.setToolTip(_translate("Dialog", "<html><head/><body><p>Telephone number</p></body></html>"))
        self.label_2.setText(_translate("Dialog", "Name"))
        self.label_5.setText(_translate("Dialog", "Profile"))

from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt, QEvent

class CheckableComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.closeOnLineEditClick = False
        self.lineEdit().installEventFilter(self)
        self.model().dataChanged.connect(self.updateLineEditField)

    def eventFilter(self,widget,event):
        if widget == self.lineEdit():
            if self.closeOnLineEditClick:
                self.hidePopup()
            else:
                self.showPopup()
            return super().eventFilter(widget,event)
        if widget == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())
                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return super().eventFilter(widget, event)

    def hidePopup(self):
        super().hidePopup()

    def addItems(self, items, itemList = None):
        for indx, text in enumerate(items):
            try:
                data = itemList[indx]
            except (TypeError, IndexError):
                data = None
            self.addItem(text,data)

    def addItem(self, text, userData=None):
        item = QStandardItem()
        item.setText(text)
        if not userData is None:
            item.setData(userData)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def updateLineEditField(self):
        text_container = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                text_container.append(self.model().item(i).text())
        text_string = ','.join(text_container)
        self.lineEdit().setText(text_string)
        

# from PyQt5.QtGui import QStrandardItem
# from PyQt5.QtCore import Qt,QEvent
# 
# class CheckableComboBox(QComboBox):
#     def __init__(self):
#         super.__init__()
#         self.setEditable(True)
#         self.lineEdit().setReadOnly(True)
#         self.closeOnLineEditClick = False
#         self.lineEdit().installEventFilter(self)
#         self.model().dataChanged.connect(self.updateLineEditFilter)
# 
#     def eventFilter(self, cb, widget,event):
#         if widget == cb.lineEdit():
#             if cb.closeOnLineEditClick:
#                 cb.hidePopup()
#             else:
#                 cb.showPopup()
#             return self.eventFilter(widget,event)
#         if widget == cb.view().viewport():
#             if event.type() == QEvent.MouseButtonRelease:
#                 index = cb.view().indexAt(event.pos())
#                 item = cb.model().item(index.row())
#                 if item.checkState() == Ot.Checked:
#                     item.setCheckState(Qt.Unchecked)
#                 else:
#                     item.setCheckState(Qt.Checked)
#                 return True
#         return self.eventFilter(widget, event)
# 
#     def hidePopup(self):
#         super().hidePopup()
# 
#     def addItems(self, items, itemList = None):
#         for indx, text in enumerate(items):
#             try:
#                 data = itemList[indx]
#             except (TypeError, IndexError):
#                 data = None
#             self.addItem(text,data)
# 
#     def addItem(self, text, userData=None):
#         item = QtStandardItem()
#         item.setText(text)
#         if not userData is None:
#             item.setData(userData)
#         item.setFlags(Qt.ItemEnabled | Qt.ItemIsUserCheckable)
#         item.setData(Qt.Unchecked, Qt.CheckStateRole)
#         self.model().appendRow(item)
# 
#     def updateLineEditField(self):
#         text_container = []
#         for i in range(self.model().rowCount()):
#             if self.model().item(i).checkState() == Qt.Checked:
#                 text_container.append(self.model().item(i).text())
#         text_string = ','.join(text_container)
#         self.lineEdit().setText(text_string)
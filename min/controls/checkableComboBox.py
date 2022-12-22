_C=None
_B=False
_A=True
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import interface.observerSubIndexList as observer
class CheckableComboBox(QComboBox,observer.Subject):
	class Delegate(QStyledItemDelegate):
		def sizeHint(self,option,index):size=super().sizeHint(option,index);size.setHeight(20);return size
	def __init__(self,subIndexList,selectedSubIndices):
		super().__init__();self._observer_list=[];self.setEditable(_A);self.lineEdit().setReadOnly(_A);self.setItemDelegate(CheckableComboBox.Delegate());self.model().dataChanged.connect(self.updateText);self.lineEdit().installEventFilter(self);self.closeOnLineEditClick=_B;self.view().viewport().installEventFilter(self);self.addItems(subIndexList)
		if selectedSubIndices!=[]:
			texts=[]
			for i in selectedSubIndices:
				texts.append(i)
				for j in range(self.model().rowCount()):
					if self.model().item(j).text()==i:self.model().item(j).setCheckState(Qt.Checked)
			text=', '.join(texts);self.lineEdit().setText(text)
	def register_observer_subIndex(self,observer):
		if observer in self._observer_list:return'Already exist observer!'
		self._observer_list.append(observer);return'Success register!'
	def remove_observer_subIndex(self,observer):
		if observer in self._observer_list:self._observer_list.remove(observer);return'Success remove!'
		return'observer does not exist.'
	def notify_observers_subIndex(self):
		for observer in self._observer_list:observer.update_subIndex()
	def eventFilter(self,object,event):
		if object==self.lineEdit():
			if event.type()==QEvent.MouseButtonRelease:
				if self.closeOnLineEditClick:self.hidePopup()
				else:self.showPopup()
				return _A
			return _B
		if object==self.view().viewport():
			if event.type()==QEvent.MouseButtonRelease:
				index=self.view().indexAt(event.pos());item=self.model().item(index.row())
				if item.checkState()==Qt.Checked:item.setCheckState(Qt.Unchecked)
				else:item.setCheckState(Qt.Checked)
				return _A
		return _B
	def showPopup(self):super().showPopup();self.closeOnLineEditClick=_A
	def hidePopup(self):super().hidePopup();self.startTimer(100);self.updateText()
	def timerEvent(self,event):self.killTimer(event.timerId());self.closeOnLineEditClick=_B
	def updateText(self):
		texts=[]
		for i in range(self.model().rowCount()):
			if self.model().item(i).checkState()==Qt.Checked:texts.append(self.model().item(i).text())
		text=', '.join(texts);self.lineEdit().setText(text);self.notify_observers_subIndex()
	def addItem(self,text,data=_C):
		item=QStandardItem();item.setText(text)
		if data is _C:item.setData(text)
		else:item.setData(data)
		item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsUserCheckable);item.setData(Qt.Unchecked,Qt.CheckStateRole);self.model().appendRow(item)
	def addItems(self,texts,datalist=_C):
		for (i,text) in enumerate(texts):
			try:data=datalist[i]
			except (TypeError,IndexError):data=_C
			self.addItem(text,data)
	def currentData(self):
		res=[]
		for i in range(self.model().rowCount()):
			if self.model().item(i).checkState()==Qt.Checked:res.append(self.model().item(i).data())
		return res
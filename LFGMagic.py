# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic
from tkinter import Tk
import os, sys, requests, json, time, winsound, webbrowser, ui #, pprint as pp

if hasattr(sys, "frozen"):
	#sys.stderr = open(os.path.dirname(__file__) + '\debug.log', 'a')
	#sys.stderr = open(os.path.expanduser('~') + '\\lfg-magic-debug.log', 'a')
	pass

def clickable(widget):
    class Filter(QtCore.QObject):
        clicked = QtCore.pyqtSignal()
        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    self.clicked.emit()
                    return True
            return False
    
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

class MyMusicThread(QtCore.QThread):
	def __init__(self, parent = None):
		QtCore.QThread.__init__(self, parent)
	
	def run(self):
		if hasattr(sys, "frozen"):
			winsound.PlaySound(os.path.dirname(sys.executable) + '\\NewPersonLFG.wav', winsound.SND_FILENAME)
		else:
			winsound.PlaySound(os.path.dirname(__file__) + '\\NewPersonLFG.wav', winsound.SND_FILENAME)
		
		self.terminate()
		self.wait()
	
class MyThread(QtCore.QThread):
	def __init__(self, parent = None, refreshInterval = 15, runOnce = False):
		QtCore.QThread.__init__(self, parent)
		
		self.runOnce = runOnce
		self.refreshInterval = refreshInterval

	def run(self):
		while True:
			QtGui.qApp.processEvents()
			self.get()
			
			if self.runOnce == True:
				self.terminate()
				self.wait()
			else:
				time.sleep(self.refreshInterval)
	
	def get(self):
		r = requests.get('http://gw2lfg.com/')
		#print(r.status_code)
		if r.status_code != 200:
			self.emit(QtCore.SIGNAL("code"), r.status_code)
		else:
			self.emit(QtCore.SIGNAL("json"), json.dumps(r.json()))

class MyWindow(QtGui.QMainWindow, ui.Ui_MainWindow):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		#uic.loadUi("untitled.ui", self)
		self.setupUi(self)
		
		self.statusBar.showMessage( 'Initiating...' )
		
		self.refresh_interval = 15 # seconds
		self.old_entries = []
		self.first_run = True
		self.copy_timer = 0
		
		self.tableWidget.setEditTriggers( QtGui.QTableWidget.NoEditTriggers )
		self.tableWidget.setSelectionMode( QtGui.QAbstractItemView.NoSelection )
		
		self.tableWidget.verticalHeader().hide()
		self.tableWidget.horizontalHeader().setResizeMode( 1, QtGui.QHeaderView.Stretch )
		
		self.tableWidget.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
		self.tableWidget.customContextMenuRequested.connect( self.menuer )
		
		self.settings = QtCore.QSettings("Ixsighter", "LFGMagic")
		
		if self.settings.value("region") != None \
		and self.settings.value("dungeon") != None \
		and self.settings.value("mode") != None:
			self.dungeoner(self.settings.value("mode"), \
				self.comboBox_2.findText(self.settings.value("dungeon"), QtCore.Qt.MatchContains))
			
			self.comboBox.setCurrentIndex(self.comboBox.findText(self.settings.value("region")))
			self.comboBox_3.setCurrentIndex(self.comboBox_3.findText(self.settings.value("mode")))
			
			if(self.settings.value("dungeon") == 'Fractals of the Mists'):
				self.comboBox_3.setDisabled( True )
		else:
			self.dungeoner()
		
		if self.settings.value("sound") != None:
			self.label.setText(
				'<html><head/><body><p><span style="font-weight:600; color:#0000ff;">Sound %s</span></p></body></html>'
				% self.settings.value("sound")
			)
		
		clickable(self.label).connect(self.muter)
		clickable(self.label_2).connect(self.creator)
		self.tableWidget.doubleClicked.connect(self.selector)
		
		self.connect(self.comboBox, QtCore.SIGNAL("currentIndexChanged(QString)"), self.getter)
		self.connect(self.comboBox_2, QtCore.SIGNAL("currentIndexChanged(QString)"), self.getter)
		self.connect(self.comboBox_3, QtCore.SIGNAL("currentIndexChanged(QString)"), self.getter)
		
		self.thread = MyThread( None, self.refresh_interval )
		self.connect(self.thread, QtCore.SIGNAL("code"), self.warner, QtCore.Qt.QueuedConnection)
		self.connect(self.thread, QtCore.SIGNAL("json"), self.processor, QtCore.Qt.QueuedConnection)
		
		self.thread.start()
	
	def menuer(self, position):
		menu = QtGui.QMenu()
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(":/copy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		
		index = self.tableWidget.indexAt(position)
		item = self.tableWidget.item(index.row(), 0)
		name = item.text()
		
		rawName  = menu.addAction( icon, "%s" % name )
		joinName = menu.addAction( icon, "/join %s" % name )
		tellName = menu.addAction( icon, "/invite %s" % name )
		
		action = menu.exec_( self.tableWidget.viewport().mapToGlobal(position) )
		
		if action == rawName:
			self.selector( index, "%s", name )
		elif action == joinName:
			self.selector( index, "/join %s", name )
		elif action == tellName:
			self.selector( index, "/invite %s", name )
	
	def dungeoner(self, type = 'Story', index = 0):
		if type == 'Story':
			dungeons = [
				"(30) Ascalonian Catacombs",
				"(40) Caudecus's Manor",
				"(50) Twilight Arbor",
				"(60) Sorrow's Embrace",
				"(70) Citadel of Flame",
				"(76) Honor of the Waves",
				"(78) Crucible of Eternity",
				"(80) The Ruined City of Arah",
				"(80) Fractals of the Mists",
			]
		elif type == 'Explorable':
			dungeons = [
				"(35) Ascalonian Catacombs",
				"(45) Caudecus's Manor",
				"(55) Twilight Arbor",
				"(65) Sorrow's Embrace",
				"(75) Citadel of Flame",
				"(80) Honor of the Waves",
				"(80) Crucible of Eternity",
				"(80) The Ruined City of Arah",
				"(80) Fractals of the Mists",
			]
		
		counter = 0
		for d in dungeons:
			self.comboBox_2.setItemText(counter, d)
			counter += 1
		
		self.comboBox_2.setCurrentIndex(index)
	
	def muter(self):
		if self.settings.value("sound") == 'on':
			self.settings.setValue("sound", 'off')
		else:
			self.settings.setValue("sound", 'on')
		
		self.label.setText(
			'<html><head/><body><p><span style="font-weight:600; color:#0000ff;">Sound %s</span></p></body></html>'
			% self.settings.value("sound")
		)
	
	def creator(self):
		webbrowser.open('http://gw2lfg.com/lfgs/new')
	
	def getter(self):
		self.statusBar.showMessage( 'Processing, please wait...' )
		
		self.dungeoner(self.comboBox_3.currentText(), self.comboBox_2.currentIndex())
		self.old_entries = []
		self.first_run = True
		
		region = str(self.comboBox.currentText())
		event_name = str(self.comboBox_2.currentText())[5:]
		event_mode = str(self.comboBox_3.currentText())
		
		self.settings.setValue("region", region)
		self.settings.setValue("dungeon", event_name)
		self.settings.setValue("mode", event_mode)
		
		if(event_name == 'Fractals of the Mists'):
			self.comboBox_3.setDisabled( True )
		else:
			self.comboBox_3.setDisabled( False )
		
		self.single = MyThread( None, self.refresh_interval, True )
		
		self.connect(self.single, QtCore.SIGNAL("code"), self.warner, QtCore.Qt.QueuedConnection)
		self.connect(self.single, QtCore.SIGNAL("json"), self.processor, QtCore.Qt.QueuedConnection)
		
		self.single.start()
	
	def selector(self, item, format = '%s', name = None):
		try:
			self.copy_timer = time.time()
			copy = format % name if name is not None else item.data()
			
			r = Tk()
			r.withdraw()
			r.clipboard_clear()
			r.clipboard_append( copy )
			r.destroy()
			
			self.statusBar.showMessage( '<%s> copied to clipboard' % copy )
		except:
			self.statusBar.showMessage( 'Could not copy clipboard data' )
	
	def warner(self, code):
		self.statusBar.showMessage('Server returned %s error code, retrying...' % code)
	
	def nicer(self, time):
		if time < 60:
			#return str(time) + ' sec.'
			return '< 1 min.'
		else:
			return str(round(time / 60)) + ' min.'
	
	def processor(self, dump):
		edit = [('null', 'None'), ('true', 'True'), ('false', 'False')]
		for search, replace in edit:
			dump = dump.replace(search, replace)

		data = eval(dump)
		reversed_data = reversed(data)
		
		region = str(self.comboBox.currentText())
		event_name = str(self.comboBox_2.currentText())[5:]
		event_mode = str(self.comboBox_3.currentText())
		
		if event_name != 'Fractals of the Mists':
			dungeon = '%s (%s)' % (event_name, event_mode)
		else:
			dungeon = event_name
		
		new_entries = []
		row_counter = 0
		
		self.tableWidget.setRowCount(0)
		
		for r in reversed_data:
			if r['region'] == region \
			and r['event_name'] == dungeon \
			and r['elapsed_time'] < 1800:
			
				row_counter += 1
				new_entries.append( int(r['id']) )
				
				self.tableWidget.insertRow(0)
				self.tableWidget.setItem(0, 0, QtGui.QTableWidgetItem( r['name'].strip() ))
				self.tableWidget.setItem(0, 1, QtGui.QTableWidgetItem( r['comment'].strip() ))
				self.tableWidget.setItem(0, 2, QtGui.QTableWidgetItem( self.nicer( r['elapsed_time']) ))
				
				self.tableWidget.resizeColumnsToContents()
				self.tableWidget.setColumnWidth(2, 55)
				
				self.tableWidget.verticalHeader().hide()
				self.tableWidget.horizontalHeader().setResizeMode( 1, QtGui.QHeaderView.Stretch )
		
		if self.settings.value("sound") == 'on':
			if ( not len( self.old_entries ) and len( new_entries ) and self.first_run == False ) \
			or ( len( self.old_entries ) and len( new_entries ) and ( new_entries[-1] - self.old_entries[-1] > 0 ) ):
				self.sound = MyMusicThread()
				self.sound.start()
		
		self.old_entries = new_entries
		self.first_run = False
		
		if time.time() > self.copy_timer + 3:
			self.statusBar.showMessage('Showing %s of %s entries' % (row_counter, len(data)))

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MyWindow()
	
	window.statusBar.setSizeGripEnabled(False)
	window.setFixedSize(680, 470)
	
	window.show()
	sys.exit(app.exec_())
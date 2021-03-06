LFG Magic
=========

LFG Magic is a small utility that works with http://gw2lfg.com/ API.  
Screenshot: http://goo.gl/B6fWF


Features
--------
- auto-refreshing list every 15 seconds
- context menu with common chat commands (```<%nick%>```, ```</join %nick%>``` and ```</invite %nick%>```)
- sound notification on new entries
- simple interface


Requirements
------------
- Python v3.3.0 or higher
- [Requests](http://docs.python-requests.org/)
- [PyQt4](http://www.riverbankcomputing.com/software/pyqt/)
- [cx_Freeze](http://cx-freeze.sourceforge.net/)

> It is also requires Microsoft Visual C++ 2010 Redistributable Package on target machines.


Usage
-----
**Build .exe**

	python setup.py build

**Build .msi**

	python setup.py bdist_msi

> Pre-builded .msi can be found at http://goo.gl/i7VB7 (64-bit versions only!)

**Other nice stuff**

	pyuic4.bat untitled.ui -o ui.py
	pyrcc4.exe resources.qrc -o resources_rc.py -py3

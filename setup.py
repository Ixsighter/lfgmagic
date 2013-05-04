import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includefiles = ['qt.conf', 'NewPersonLFG.wav', 'imageformats']
includes = []
excludes = []
packages = []

#`shortcutDir` can be:
#ProgramMenuFolder 
#DesktopFolder

setup(
    name = 'LFG Magic',
    version = '0.1.4',
    description = 'LFG Magic utility',
    author = 'Ixsighter',
    #author_email = 'root@x-root.org',
	#package_dir = {'': 'lib'},
    options = {'build_exe': {'excludes': excludes, 'packages': packages, 'include_files': includefiles, 'icon': "file.ico"}}, 
    executables = [Executable(script = 'LFGMagic.py', base = base, shortcutName = 'LFG Magic', shortcutDir = 'DesktopFolder')]
)
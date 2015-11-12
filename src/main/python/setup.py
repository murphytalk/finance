# -*- coding: utf-8 -*-
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

from cx_Freeze import setup, Executable
from os.path import expanduser
DEPLOY=expanduser("~")+'/DEPLOYMENT/bin'

build_exe_opts = {"silent": False,
                  "packages": ['lxml', 'gzip'],
                  "build_exe":DEPLOY 
                 }
executables = [
    Executable('scraper.py'),
    Executable('financial_data.py'),
    Executable('scrap_to_db.py')
]

setup(name='finance',
      version='0.1',
      description='my finance package',
      options={"build_exe": build_exe_opts},
      executables=executables
      )

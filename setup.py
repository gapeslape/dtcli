#!/usr/bin/env python

from distutils.core import setup

setup(name='dtcli',
      version='0.1',
      description='Django Template Command Line Interface',
      author='Gasper Setinc',
      author_email='gasper.setinc@gmail.com',
      packages=['tags', 'tags/templatetags'],
	  scripts=['dtcli',]
     )

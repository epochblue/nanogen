#!/usr/bin/env python

from setuptools import setup

requires = ['jinja2 >= 2.7', 'markdown', 'pyyaml', 'docopt']
entry_points = {
    'console_scripts': ['gin = gin:main']
}

setup(name='gin',
      version='0.3.0',
      description='A very small static site generator',
      author='Bill Israel',
      author_email='bill.israel@gmail.com',
      license='MIT',
      url='https://github.com/epochblue/gin',
      py_modules=['gin'],
      install_requires=requires,
      entry_points=entry_points,
      keywords=['ssg', 'generator', 'static site generator', 'blog'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent'
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ])

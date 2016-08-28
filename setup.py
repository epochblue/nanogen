import os
from setuptools import setup

from version import version

entry_points = {
    'console_scripts': ['nanogen = cli:cli']
}

long_description = open(
    os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    )
).read()

setup(name='nanogen',
      version=version,
      description='A very small static blog generator',
      long_description=long_description,
      author='Bill Israel',
      author_email='bill.israel@gmail.com',
      license='MIT',
      url='https://github.com/epochblue/nanogen',
      py_modules=['nanogen'],
      install_requires=[
          'click==6.6',
          'mistune==0.7.3',
          'Jinja2==2.8',
          'Pygments==2.1.3'
      ],
      entry_points=entry_points,
      keywords=['command line', 'static generator', 'blog'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ])

import os
from setuptools import setup

from nanogen.version import version

install_requires = [
    'click==6.7',
    'mistune==0.8.3',
    'Jinja2==2.10',
    'Pygments==2.2.0'
]

dev_requires = [
    'pytest==3.4.1'
]

entry_points = {
    'console_scripts': ['nanogen = nanogen.cli:cli']
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
      packages=['nanogen'],
      install_requires=install_requires,
      extras_require={
          'dev': dev_requires,
      },
      entry_points=entry_points,
      keywords=['command line', 'static generator', 'blog'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ])

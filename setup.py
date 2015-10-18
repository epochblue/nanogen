import os
from setuptools import setup
from nanogen import __version__

entry_points = {
    'console_scripts': ['nanogen = nanogen.nanogen:cli']
}

long_description = open(
    os.path.join(
        os.path.dirname(__file__),
        'README.md'
    )
).read()

setup(name='nanogen',
      version=__version__,
      description='A very small static site generator',
      long_description=long_description,
      author='Bill Israel',
      author_email='bill.israel@gmail.com',
      license='MIT',
      url='https://github.com/epochblue/nanogen',
      packages=['nanogen'],
      install_requires=[
          'click==5.1',
          'mistune==0.7.1',
          'Jinja2==2.8',
          'MarkupSafe==0.23',
          'Pygments==2.0.2',
          'PyYAML==3.11'
      ],
      entry_points=entry_points,
      keywords=['ssg', 'generator', 'static site generator', 'blog'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ])

from distutils.core import setup


try:
    import argparse
except ImportError:
    print "Module argparse is required by idl. Please install it and try again."

try:
    import json
except ImportError:
    print "Module json is required by idl. Please install it and try again."

try:
    import urllib
    import urllib2
except ImportError:
    print "Modules urllib and urllib2 are required by idl. Please install them and try again."



setup(name='idli',
      version='0.1',
      description='Bug tracker interface',
      author='Chris Stucchio',
      author_email='stucchio@gmail.com',
      license='GPL v3',
      url='http://github.com/stucchio/Idli',
      classifiers=[
          'Development Status :: 3 - Alph',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GPL V3',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Bug Tracking',
          ],
      package_dir = { 'idli' : 'idli' },
      packages = ['idli', 'idli.backends'],
      scripts = ['scripts/idli',],
     )


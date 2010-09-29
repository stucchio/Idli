from distutils.core import setup


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


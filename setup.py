import os

from setuptools import setup

# use smart versioning system, s. e.g. django-zotero

setup(name='lara',
      version='0.0.3',
      zip_safe=False,  # eggs are the devil.
      description='LARA - Laboratory Automation Robotic Assistant.',
      long_description=open(os.path.join(os.path.dirname(__file__),
                                         'README.rst')).read(),
      author='mark doerr',
      author_email='mark.doerr@uni-greifswald.de',
      url='https://github.com/LARAsuite/lara',
      packages=[''],
      include_package_data=True,
      keywords='lab automation, scientific database, data evaluation, data visualisation, LIMS, robots',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      test_suite='',
      classifiers=['Development Status :: 1 - Development',
                   'Environment :: python',
                   'Framework :: python',
                   'Framework :: python :: 2.7',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GPL3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Topic :: Utilities'],
      )

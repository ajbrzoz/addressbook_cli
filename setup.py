try:
    from setuptools import setup
except ImportError:
    from disutils.core import setuptools
    
config = {
    'description': 'AddressBook 1.0 - command-line contact manager',
    'author': 'Anna Brzozowska',
    'url': '',
    'author_email': 'brzozowskaanna5@gmail.com',
    'version': '1.0',
    'install_requires': [],
    'packages': ['addressbook'],
    'scripts': [],
    'name': 'AddressBook'
}

setup(**config)
from setuptools import setup

setup(
	name = "automatoetry",
	version = "1.0",
	description = "Automatoetry - Automatized Haiku Poetry with genetic algorithms and Python",
	author = "Tobias Radloff",
	author_email = "mail@tobias-radloff.de",
	url = "http://www.python.org/sigs/distutils-sig/",
	install_requires = [
		'web.py >= 0.37',
		'libleipzig',
		'MySQL-python',
		'Markdown >= 2',
	],
)

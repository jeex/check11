from setuptools import setup, find_packages

# IMPORTANT, also change VERSION in web and check11.py

setup(
	name='check11',
	version='0.1.0',
	packages=find_packages(include=['cpnits_check11', 'cpnits_check11.*']),
	install_requires=[
		'PyYAML',
		'requests',
		'colorama',
		'importlib',
		'pytest',
	],
	entry_points={
	    'console_scripts': [
	        'check11=cpnits_check11.check11:run'
	    ]
	},	
)

# https://xebia.com/blog/a-practical-guide-to-using-setup-py/

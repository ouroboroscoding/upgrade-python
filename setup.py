from setuptools import setup

with open('README.md', 'r') as oF:
	long_description=oF.read()

setup(
	name='upgrade_oc',
	version='1.1.0',
	description='Generic functions for handling upgrading services',
	long_description=long_description,
	long_description_content_type='text/markdown',
	project_urls={
		'Source': 'https://github.com/ouroboroscoding/upgrade-python',
		'Tracker': 'https://github.com/ouroboroscoding/upgrade-python/issues'
	},
	keywords=[ 'upgrade', 'upgrading', 'automatic' ],
	author='Chris Nasr - Ouroboros Coding Inc.',
	author_email='chris@ouroboroscoding.com',
	license='CUSTOM',
	packages=[ 'upgrade_oc' ],
	python_requires='>=3.10',
	install_requires=[
		"strings-oc>=1.0.7,<1.1",
		"tools-oc>=1.2.5,<1.3"
	],
	zip_safe=True
)
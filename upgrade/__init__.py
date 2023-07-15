# coding=utf8
""" Upgrade

Methods to upgrade services
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-07-12"

__all__ = ['set_latest', 'upgrade']

# Ouroboros imports
from strings import from_file, to_file, version_compare
from tools import lfindi

# Python imports
from importlib import import_module
from functools import cmp_to_key
from os import path, scandir
import re

# Constants
UPGRADE_SCRIPT = re.compile('^v\d+_\d+_\d+_v\d+_\d+_\d+\.py$')

def _get_versions(module_path) -> list[dict]:
	"""Get Versions

	Returns a list of the upgrade versions currently available in the given \
	folder.

	Arguments:
		module_path (str): The path to the module

	Returns:
		list[dict]
	"""

	# Get the current versions from the upgrades directory
	lVersions = []
	for o in scandir('%s/upgrades' % module_path):
		if o.is_file() and UPGRADE_SCRIPT.match(o.name):
			l = [s.replace('_', '.') for s in o.name[1:-3].split('_v')]
			lVersions.append({
				'module': o.name[:-3],
				'at': l[0],
				'to': l[1]
			})

	# Sort them by 'at'
	lVersions.sort(key=cmp_to_key(lambda a, b: version_compare(a['at'], b['at'])))

	# Return the versions found
	return lVersions

def _version_prompt(versions: list[dict]):
	"""Version Prompt

	Keeps asking the user for a version from the list until a satisfactory
	answer is delivered

	Arguments:
		versions (dict[]): The list of upgrades available
		prompt (str): The message to deliver to the user

	Returns:
		int | None
	"""

	# Loop until we have the right version
	while True:

		# Display the current list
		for i in range(len(versions)):
			print('[%d]: %s' % (i, versions[i]['at']))
		print('[q]: quit')
		sIndex = input('Please select the version to start from: ')

		# If it's 'q'
		if sIndex == 'q':
			return None

		# If it not an int
		try:
			iIndex = int(sIndex)
		except ValueError:
			print('Invalid version, please select a number from 0 to %d, or "q" to quit' % (len(versions) - 1))
			continue

		# If it's to long
		if iIndex > len(versions):
			print('Invalid version, please select a number from 0 to %d, or "q" to quit' % (len(versions) - 1))
			continue

		# Return the index from the list of versions
		return iIndex

def set_latest(data_path: str, module_path: str) -> bool:
	"""Set Latest

	Sets the current version to the last upgradable version. This is useful if
	the system is being installed from scratch and will already be up to date

	Arguments:
		data_path (str): The path where the version file can be stored
		module_path (str): The path to the module

	Returns:
		bool
	"""

	# Using the module path, get the name of the file
	sFile = '%s/%s.ver' % (
		data_path,
		path.basename(module_path)
	)

	# Get the versions available, and store the "to" of the last one
	return to_file(
		sFile,
		_get_versions(module_path)[-1]['to']
	)

def upgrade(data_path: str, module_path: str) -> int:
	"""Upgrade

	Upgrades the tables and other data from one version to the next

	Arguments:
		data_path (str): The path where the version file can be stored
		module_path (str): The path to the module

	Returns:
		int
	"""

	# Get the module name
	sModule = path.basename(module_path)

	# Using the module path, get the name of the file
	sFile = '%s/%s.ver' % (data_path, sModule)

	# Get the current version
	sVersion = from_file(sFile)
	iVersion = -1

	# Get the current versions from the upgrades directory
	lVersions = _get_versions(module_path)

	# If we have no version
	if not sVersion:

		# Notify the user we have no version
		print('No version found in the file (%s)' % sFile)

		# Ask them to provide it
		iVersion = _version_prompt(lVersions)

		# If they deciced to quit
		if iVersion is None:
			return 0

	# Else, make sure the version matches something we have
	else:

		# If it's the last version
		if sVersion == lVersions[-1]['to']:
			print('Already up to date')
			return 0

		# Find the index from the stored version
		iVersion = lfindi(lVersions, 'at', sVersion)

		# If it doesn't exist
		if iVersion == -1:

			# Notify the user we have no version
			print('The stored version "%s" doesn\'t match any available' % sVersion)

			# Ask them to provide it
			iVersion = _version_prompt(lVersions)

			# If they deciced to quit
			if iVersion is None:
				return 0

	print('Current version: %s' % lVersions[iVersion]['at'])

	# Starting at the version we have selected, run through each of the
	#	remaining to update to the latest
	while iVersion < len(lVersions):

		# Load the module
		oVer = import_module('%s.upgrades.%s' % (
			sModule,
			lVersions[iVersion]['module']
		))

		# Run the the upgrade, if it fails
		if not oVer.run():
			print('Failed')
			return 1

		# Store the new "at" version using the "to" from this one
		to_file(sFile, lVersions[iVersion]['to'])

		# Increase the version and loop back around
		iVersion += 1

	# Notify
	print('Success')

	# Return OK
	return 0
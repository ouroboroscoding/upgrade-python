# coding=utf8
""" Upgrade

Methods to upgrade services
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-07-12"

# Limit imports
__all__ = [
	'set_latest', 'uninstall', 'upgrade', 'UpgradeMessages',
	'UpgradeScriptRegex'
]

# Ouroboros imports
from strings import from_file, to_file, version_compare
from tools import lfindi

# Python imports
from importlib import import_module
from functools import cmp_to_key
from os import path, remove as osremove, scandir
from sys import stderr
from typing import List

# Import types
from upgrade_oc.types import UpgradeMessages, UpgradeMode, UpgradeScriptRegex

# Default messages
_default_messages = UpgradeMessages()

def _get_versions(
	module_path: str,
	messages: UpgradeMessages
) -> List[dict]:
	"""Get Versions

	Returns a list of the upgrade versions currently available in the given \
	folder.

	Arguments:
		module_path (str): The path to the module
		messages (UpgradeMessages): The messages to display to the user, \
			specifically `no_path`

	Returns:
		list[dict]
	"""

	# Get the current versions from the upgrades directory
	lVersions = []
	try:
		sPath = '%s/upgrades' % module_path
		for o in scandir(sPath):
			if o.is_file() and UpgradeScriptRegex.match(o.name):
				l = [s.replace('_', '.') for s in o.name[1:-3].split('_v')]
				lVersions.append({
					'module': o.name[:-3],
					'at': l[0],
					'to': l[1]
				})
	except FileNotFoundError as e:
		print(messages.no_path % e.filename, file = stderr)
		return []

	# Sort them by 'at'
	lVersions.sort(
		key=cmp_to_key(lambda a, b: version_compare(a['at'], b['at']))
	)

	# Return the versions found
	return lVersions

def _version_prompt(
	versions: List[dict],
	messages: UpgradeMessages
):
	"""Version Prompt

	Keeps asking the user for a version from the list until a satisfactory
	answer is delivered

	Arguments:
		versions (dict[]): The list of upgrades available
		messages (UpgradeMessages): The messages to display to the user, \
			specifically `select` and `select_invalid`

	Returns:
		int | None
	"""

	# If no versions were passed return immediately as we can't do anything
	if not versions:
		return None

	# Loop until we have the right version
	while True:

		# Display the current list
		for i in range(len(versions)):
			print('[%d]: %s' % (i, versions[i]['at']))
		print('[q]: quit')
		sIndex = input(messages.select)

		# If it's 'q'
		if sIndex == 'q':
			return None

		# If it not an int
		try:
			iIndex = int(sIndex)
		except ValueError:
			print(messages.select_invalid % (len(versions) - 1))
			continue

		# If it's to long
		if iIndex > len(versions):
			print(messages.select_invalid % (len(versions) - 1))
			continue

		# Return the index from the list of versions
		return iIndex

def set_latest(
	data_path: str,
	module_path: str,
	initial: str = '1.0.0',
	messages: UpgradeMessages = _default_messages
) -> bool:
	"""Set Latest

	Sets the current version to the last upgradable version. This is useful if \
	the system is being installed from scratch and will already be up to date. \
	If no upgrade scripts are found, uses the `initial` value which has a \
	default of "1.0.0"

	Arguments:
		data_path (str): The path where the version file can be stored
		module_path (str): The path to the module
		initial (str): Optional, the initial version to set the module to if \
			no upgrade scripts are found
		messages (UpgradeMessages): The messages to display to the user, \
			specifically `no_path`

	Returns:
		bool
	"""

	# Get the current versions
	lVersions = _get_versions(module_path, messages)

	# If there's none, use the initial argument
	if not lVersions:
		sVersion = initial

	# Else, use the 'to' of the last version
	else:
		sVersion = lVersions[-1]['to']

	# Using the module path, get the name of the file, get the versions
	#	available, and store the "to" of the last one
	return to_file(
		'%s/%s.ver' % ( data_path, path.basename(module_path) ),
		sVersion
	)

def uninstall(
	data_path: str,
	module_path: str,
	messages: UpgradeMessages = _default_messages
) -> bool:
	"""Uninstall

	Removes the version file

	Arguments:
		data_path (str): The path where the version file can be stored
		module_path (str): The path to the module
		messages (UpgradeMessages): The messages to display to the user, \
			specifically `no_file`

	Returns:
		bool
	"""

	# Using the module path, get the name of the file, then delete it and return
	#	True
	try:
		osremove('%s/%s.ver' % (
			data_path,
			path.basename(module_path)
		))
		return True

	# If the file is not found, return False
	except FileNotFoundError as e:
		print(messages.no_file % e.filename, file = stderr)
		return False

def upgrade(
	data_path: str,
	module_path: str,
	mode: UpgradeMode = 'module',
	messages: UpgradeMessages = _default_messages
) -> int:
	"""Upgrade

	Runs the upgrade scripts one at a time until the version is at the latest

	Arguments:
		data_path (str): The path where the version file can be stored
		module_path (str): The path to the module
		mode (UpgradeMode): The mode to run in, 'module' or 'project'
		messages (UpgradeMessages): The messages to use in communicating to \
			the user of success or failures

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
	lVersions = _get_versions(module_path, messages)

	# If we got no versions
	if not lVersions:
		print(messages.none, file = stderr)
		return 0

	# If we have no version
	elif not sVersion:
		if sVersion is None:
			print(messages.no_file % sFile, file = stderr)
		else:
			print(messages.invalid % str(sVersion), file = stderr)

		# Ask them to provide it
		iVersion = _version_prompt(lVersions, messages)

		# If they deciced to quit
		if iVersion is None:
			return 0

	# Else, make sure the version matches something we have
	else:

		# If it's the last version
		if sVersion == lVersions[-1]['to']:
			print(messages.up_to_date)
			return 0

		# Find the index from the stored version
		iVersion = lfindi(lVersions, 'at', sVersion)

		# If it doesn't exist
		if iVersion == -1:

			# Notify the user we have no version
			print(messages.invalid % sVersion, file = stderr)

			# Ask them to provide it
			iVersion = _version_prompt(lVersions, messages)

			# If they deciced to quit
			if iVersion is None:
				return 0

	# Print the current version
	print(messages.current % lVersions[iVersion]['at'])

	# Starting at the version we have selected, run through each of the
	#	remaining to update to the latest
	while iVersion < len(lVersions):

		# If we're in module mode
		if mode == 'module':

			# Load the module
			oVer = import_module('%s.upgrades.%s' % (
				sModule,
				lVersions[iVersion]['module']
			))

		# Else, if we're in project mode
		elif mode == 'project':

			# Load the module
			oVer = import_module('upgrades.%s' % lVersions[iVersion]['module'])

		# Run the the upgrade, if it fails
		if not oVer.run():
			print(messages.failed, file = stderr)
			return 1

		# Store the new "at" version using the "to" from this one
		to_file(sFile, lVersions[iVersion]['to'])

		# Increase the version and loop back around
		iVersion += 1

	# Notify
	print(messages.success)

	# Return OK
	return 0
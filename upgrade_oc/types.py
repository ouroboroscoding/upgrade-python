# coding=utf8
""" Types

The types for the upgrade_oc module
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2025-03-14"

# Limit imports
__all__ = [ 'UpgradeMessages', 'UpgradeMode', 'UpgradeScriptRegex' ]

# Python modules
from dataclasses import dataclass
import re
from typing import Literal

@dataclass
class UpgradeMessages:
	"""" Upgrade Messages

	Type to pass to upgrade if you need to modify the language of messages to \
	the user
	"""

	current: str = 'Current version: %s'
	"""Current
	Displays the current version based on the stored value. Requires a %s for \
	the stored version."""

	failed: str = 'Failed'
	"""Failed
	Some error occurred in a version's run() method. Counter to `success`."""

	invalid: str = 'The stored version "%s" does not match any available'
	"""Invalid
	The version found in the version file does not anything in the versions \
	available from the upgrades directory. Requires a %s for the stored version.
	"""

	none: str = 'No versions available, unable to upgrade.'
	"""None
	No version files found in the upgrades directory"""

	no_file: str = 'File "%s" not found.'
	"""No File
	No version file found in the data directory. Requires a %s for the name of \
	the file."""

	no_path: str = 'Folder "%s" not found, no versions available.'
	"""No Path
	Nothing was found in the modules upgrades directory. Requires a %s for the \
	upgrades directory."""

	select: str = 'Please select the version to start from: '
	"""Select
	The prompt to select a version by a number in a list"""

	select_invalid: str = 'Invalid version, please select a number from 0 to %d, or "q" to quit.'
	"""Select Invalid
	The user made a bad version selection. Requires a %d in it for the count \
	of versions available."""

	success: str = 'Success'
	"""Success
	Finished upgrading without error."""

	up_to_date: str = 'Already up to date'
	"""Up To Date
	Module/project is already up to date."""

UpgradeMode = Literal['module'] | Literal['project']
"""The mode for set_latest and upgrade"""

UpgradeScriptRegex = re.compile('^v\d+_\d+_\d+_v\d+_\d+_\d+\.py$')
"""The regular expression for the upgrade script format"""

# Upgrade by Ouroboros Coding Inc.
[![pypi version](https://img.shields.io/pypi/v/upgrade_oc.svg)](https://pypi.org/project/upgrade_oc) ![MIT License](https://img.shields.io/pypi/l/upgrade_oc.svg)

Methods to easily update data associated with services and projects created by
Ouroboros Coding Inc. to their latest version.

## Installing
```bash
pip install upgrade_oc
```

## Using
Upgrade comes with a class, 3 methods, and a compiled regular expression.

### UpgradeMessages
In order to support additional languages, or simply different ways to put
things, you can overwrite any of the message strings used by upgrade via your
own UpgradeMessages instance.

The current default messages can be found in the [types.py](./upgrade_oc/types.py)
file. Since each variable in the class has a default, you can pick and choose
which messages you want to replace.

```python
from upgrade_oc import UpgradeMessages

# Override just no_file and no_path
my_messages = UpgradeMessages(
	no_file = ('#' * 40) + '\nThe file at %s could not be found.\n' + ('#' * 40)
	no_path = ('#' * 40) + '\nNo path %s exists.\n' + ('#' * 40)
)
```

### set_latest
Sets the current version to the last upgradable version. This is useful if the
system is being installed from scratch and will already be up to date. If no
upgrade scripts are found, uses the `initial` value which has a default of
"1.0.0"

install.py
```python
from upgrades_oc import set_latest
from pathlib import Path

set_latest(
  '../data',
  Path(__file__).parent.resolve()
)
```

Assuming a module structure of
```
├── my_module/
│   ├── install.py
│   ├── uninstall.py
│   ├── upgrade.py
│   └── upgrades/
│       ├── __init__.py
│       ├── v1_0_1_v1_1_0.py
│       ├── v1_1_0_v1_1_1.py
│       ├── v1_1_1_v2_2_0.py
│       └── v2_2_0_v2_3_0.py
└── data/
```

This would create a new file `data/my_module.ver` which contained the value

```
2.3.0
```

If we wanted to substitute the messages for our own

```python
set_latest(
  '../data',
  Path(__file__).parent.resolve(),
  messages = my_messages
)
```

### uninstall
Removes the version file. In the previous example, calling uninstall would
remove the `data/my_module.ver` file from the system

uninstall.py
```python
from upgrades_oc import set_latest
from pathlib import Path

uninstall(
  '../data',
  Path(__file__).parent.resolve(),
  messages = my_messages
)
```

### upgrade
Runs the upgrade scripts found in the upgrades directory one at a time from the
current version until we achieve the latest. Keep this in mind if you plan on
supporting upgrading multiple versions at once, as any imports in the upgrade
scripts will need to still be available and run as expected at the time of the
upgrade scripts writing. This is not an issue if you choose to change version,
upgrade, change version again, and upgrade again.

upgrade.py
```python
from upgrade_oc import upgrade
from pathlib import Path

upgrade(
	'../data',
	Path(__file__).parent.resolve(),
	messages = my_messages
)
```

#### upgrade on projects
If you are running upgrade on a project, something that can not reference
itself, be sure to set the mode flag to 'project' so that upgrade knows to look
for the upgrades folder in the current working directory.

```
├── my_project
│   ├── .data/
│   ├── upgrade.py
│   └── upgrades/
│       ├── __init__.py
│       ├── v1_0_0_v1_1_0.py
│       ├── v1_1_0_v1_1_1.py
```

upgrade.py
```python
from upgrade_oc import upgrade
from pathlib import Path

upgrade(
	'./.data',
	Path(__file__).parent.resolve(),
	mode = 'project'
	messages = my_messages
)
```

Which would result in the file `my_project/.data/my_project.ver` containing
```
1.1.1
```

### UpgradeScriptRegex
This compiled regular expression is represents the file name structure for
upgrade scripts. Described below

### Upgrade Script format
A version file is in the format, *version to convert from* underscore *version
to convert to*, python extension. Where the periods in the version are also
underscores.

So if we were at version 1.0.0, and wanted to go to version 1.1.0:
```
v1_0_0_v1_1_0.py
```

or from 1.1.0 to 1.1.1
```
v1_1_0_v1_1_1.py
```

Versions have to be sequencial, and one must tie into the previous, but you are
not required to enter every version of your software, just the ones that require
something to be run in order to upgrade. The following list

```
│   └── upgrades/
│       ├── __init__.py
│       ├── v1_0_0_v1_0_1.py
│       ├── v1_0_1_v1_0_2.py
│       ├── v1_0_2_v1_0_3.py
│       ├── v1_0_3_v1_0_4.py
```

Is as valid as
```
│   └── upgrades/
│       ├── __init__.py
│       ├── v1_0_0_v2_34_1.py
│       ├── v2_34_1_v2_48_6.py
│       ├── v2_48_6_v10_0_0.py
│       ├── v10_0_0_v10_0_1.py
```

### Upgrade Script internals
The only thing required in an upgrade script is a `run()` method that returns
`True` on success or `False` on failure.

v2_48_6_v10_0_0.py
```python
"""2.48.6 to 10.0.0
This upgrade script will convert to 10.0.0 from 2.48.6
"""
def run():
	try:
		""" do stuff to upgrade """
		return True
	except Exception:
		return False
```
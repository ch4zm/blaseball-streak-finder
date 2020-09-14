# `bump_version_number.py`

This program will parse the `__init__.py` file of the project and
increment the `__version__` variable by a major, minor, or patch
amount:

```
bump_version_number.py --major
bump_version_number.py --minor
bump_version_number.py --patch
```

Major will update the leading digit of the version number: 0.5 -> 1.0, 1.1.1 -> 2.0.0

Minor will update the middle digit of the version number: 0.2.5 -> 0.3.0, 1.1.1 -> 1.2.0

Patch will update the last digit of the version number: 0.2.5 -> 0.2.6, 1.1.1 -> 1.1.2

# `deploy_new_version.sh`

This script creates a virtual Python environment, installs the package
and its dependencies into it, and runs through all of the steps to build,
check, install, and upload the next version of the software.

Pass a flag to indicate whether it should update the major, minor, or patch version:

```
deploy_new_version.sh --major
deploy_new_version.sh --minor
deploy_new_version.sh --patch
```

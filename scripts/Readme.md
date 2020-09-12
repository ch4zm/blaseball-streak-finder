# `bump_version_number.py`

This program will parse the `__init__.py` file of the project and
increment the `__version__` variable by the smallest amount possible
(so 0.5 will become 0.6, 0.5.1 will become 0.5.2, etc.)

# `deploy_minor_version.sh`

This script creates a virtual Python environment, installs the package
and its dependencies into it, and runs through all of the steps to build,
check, install, and upload the next version of the software.


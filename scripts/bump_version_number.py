import os
import re

"""
This script bumps the version number in the most minor way possible.
If your version number is 0.1, it will bump it to 0.2.
If your version number is 0.0.1, it will bump it to 0.0.2.
For anything more major, do it yourself!
"""

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
init_path = os.path.abspath(os.path.join(root_path, '..', 'blaseball_core_game_data'))
INIT = "__init__.py"

with open(os.path.join(init_path, INIT), 'r') as f:
    content = f.read()

lines = content.split("\n")
for line in lines:
    m = re.search(r'__version__ = "(.*)"', line.strip())
    if m is not None:
        version_str = m.group(1)
        versions = [int(j) for j in version_str.split(".")]
        versions[-1] += 1
        new_version_str = ".".join([str(j) for j in versions])
        content = re.sub(version_str, new_version_str, content)
        break

with open(os.path.join(init_path, INIT), 'w') as f:
    f.write(content)

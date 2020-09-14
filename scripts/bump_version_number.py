import sys
import os
import re
import argparse

"""
This script bumps the minor version number.
If your version number is 0.1, it will bump it to 0.2.
If your version number is 0.0.1, it will bump it to 0.0.2.
"""


pkg_name = 'interesting_blaseball_games'


def usage():
    print("")
    print("Bump version number script:")
    print("")
    print("Usage:")
    print("    python bump_version_number.py [--major,--minor]")
    print("")
    print("Use the --minor flag to bump the minor version (0.1 -> 0.2, 1.5.7 -> 1.5.8, etc)")
    print("Use the --major flag to bump the major version (0.1 -> 1.0, 1.5.7 -> 2.0.0, etc)")
    print("")
    sys.exit(1)

def main(args):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    init_path = os.path.abspath(os.path.join(root_path, '..', pkg_name))
    INIT = "__init__.py"
    
    with open(os.path.join(init_path, INIT), 'r') as f:
        content = f.read()
    
    lines = content.split("\n")
    for line in lines:
        m = re.search(r'__version__ = "(.*)"', line.strip())
        if m is not None:
            version_str = m.group(1)
            versions = [int(j) for j in version_str.split(".")]

            if args.major:
                versions[0] += 1
                for i in range(1,len(versions)):
                    versions[i] = 0
            elif args.minor:
                versions[1] += 1 
                if len(versions)>2:
                    for i in range(2, len(versions)):
                        versions[i] = 0
            elif args.patch:
                versions[-1] += 1
            new_version_str = ".".join([str(j) for j in versions])
            content = re.sub(version_str, new_version_str, content)
            break
    
    with open(os.path.join(init_path, INIT), 'w') as f:
        f.write(content)
    
    print(new_version_str)

if __name__=="__main__":

    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group()
    g.add_argument('--patch',
                   required=False,
                   default=False,
                   action='store_true',
                   help='Bump the patch version (0.1.0 -> 0.1.1, 1.5.7 -> 1.5.8, etc)')
    g.add_argument('--minor',
                   required=False,
                   default=False,
                   action='store_true',
                   help='Bump the minor version (0.1 -> 0.2, 1.5.7 -> 1.6.0, etc)')
    g.add_argument('--major',
                   required=False,
                   default=False,
                   action='store_true',
                   help='Bump the major version (0.1 -> 1.0, 1.5.7 -> 2.0.0, etc)')

    args = p.parse_args(sys.argv[1:])
    if not args.patch and not args.minor and not args.major:
        usage()

    main(args)

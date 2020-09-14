#!/bin/sh
set -e

# bump version num in src code
while test $# -gt 0; do
    case "$1" in
        -h|--help)
            echo "deploy_new_version.sh - deploy a new version of this Python package to PyPi"
            echo " "
            echo "deploy_new_version.sh [flags]"
            echo " "
            echo "options:"
            echo "-h, --help                show brief help"
            echo "--major                   deploy a new major version (x.0.0)"
            echo "--minor                   deploy a new minor version (0.x.0)"
            echo "--patch                   deploy a new patch version (0.0.x)"
            exit 0
            ;;
        --major)
            BUMP_ARGS="--major"
            shift
            ;;
        --minor)
            BUMP_ARGS="--minor"
            shift
            ;;
        --patch)
          BUMP_ARGS="--patch"
          shift
          ;;
        *)
          break
          ;;
    esac
done

WORKDIR=$PWD
DIRNAME=$(dirname $0)
SCRIPTDIR=${WORKDIR}/${DIRNAME:2}
ROOTDIR=$SCRIPTDIR/..

# make sure we are on correct branch
cd $ROOTDIR
CB=$(git branch --show-current)
if [[ "$CB" != "master" ]]; then
    echo "Error: you are not on the master branch, you are on branch $CB"
    echo "Merge your changes into master before continuing"
    exit 1;
fi

echo "Script dir: $SCRIPTDIR"

cd $ROOTDIR
rm -fr $ROOTDIR/.releasevp

# make and enter virtualenv
virtualenv -p python3.6 $ROOTDIR/.releasevp
source $ROOTDIR/.releasevp/bin/activate

VERSION=$($ROOTDIR/.releasevp/bin/python $ROOTDIR/scripts/bump_version_number.py $BUMP_ARGS)
echo "Bumped source code to $VERSION"

echo "Making things..."
make clean

# install requirements
make requirements || { echo "Failed make requirements step"; exit 1; }
make dev || { echo "Failed make dev step"; exit 1; }

# build and upload
make clean
make build || { echo "Failed make build step"; exit 1; }
make dist || { echo "Failed make dist step"; exit 1; }
make distcheck || { echo "Failed make distcheck step"; exit 1; }

echo "Everything checks out. Uploading to testpypi, then pypi..."
make testpypi || { echo "Failed make testpypi step"; exit 1; }
make pypi || { echo "Failed make pypi step"; exit 1; }
echo "Done!"

echo "Making git tag"
git add interesting_blaseball_games
git commit interesting_blaseball_games -m "auto-update to version $VERSION"
git tag $VERSION
git push --tags ch4zm master

# Clean up
deactivate
rm -fr $ROOTDIR/.releasevp

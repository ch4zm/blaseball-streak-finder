#!/bin/sh
set -e

WORKDIR=$PWD
DIRNAME=$(dirname $0)
SCRIPTDIR=${WORKDIR}/${DIRNAME:2}
ROOTDIR=$SCRIPTDIR/..
echo "Script dir: $SCRIPTDIR"

cd $ROOTDIR
rm -fr $ROOTDIR/.releasevp

# make sure we are on correct branch
git checkout master

# make and enter virtualenv
virtualenv -p python3.6 $ROOTDIR/.releasevp
source $ROOTDIR/.releasevp/bin/activate

# bump version num in src code
VERSION=$($ROOTDIR/.releasevp/bin/python $ROOTDIR/scripts/bump_version_number.py)
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
git add streak_finder
git commit streak_finder -m "auto-update to version $VERSION"
git tag $VERSION
git push --tags ch4zm master

# Clean up
deactivate
rm -fr $ROOTDIR/.releasevp

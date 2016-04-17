#!/bin/bash

set -e

# add git auth
eval "$(ssh-agent -s)" #start the ssh agent
chmod 600 .travis/archiver_rsa # this key should have push access
ssh-add .travis/archiver_rsa

git config user.email "<hello@openbylaws.org.za>"
git config user.name "OpenByLaws (via TravisCI)"
git commit -m "Updates from Indigo via TravisCI"
git remote set-url origin git@github.com:longhotsummer/za-by-laws.git
git push

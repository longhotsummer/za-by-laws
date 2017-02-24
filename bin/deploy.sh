#!/bin/bash
set -e -x

if [ "${TRAVIS_PULL_REQUEST}" = "false" ] && [ "${TRAVIS_BRANCH}" = "build" ]; then
  # switch to gh-pages branch
  git config user.email "<hello@openbylaws.org.za>"
  git config user.name "OpenByLaws (via TravisCI)"
  git fetch origin master
  git checkout FETCH_HEAD
  git checkout -b master

  # update the index file and rebuild site data
  curl http://code4sa-gazettes.s3.amazonaws.com/archive/index/gazette-index-latest.jsonlines -O
  python bin/build-index.py

  # ensure the site builds
  bundle install
  bundle exec jekyll build

  # save changes
  git add _data _gazettes
  git commit -m "Updates from Indigo via TravisCI" || exit 0

  # now update gh-pages branch on github
  echo "Deploying to GitHub"

  # add git auth
  eval "$(ssh-agent -s)" #start the ssh agent
  set +x
  openssl aes-256-cbc -K $encrypted_c57ccc1bf147_key -iv $encrypted_c57ccc1bf147_iv -in deploy_key.enc -out deploy_key -d
  set -x
  chmod 600 deploy_key # this key should have push access
  ssh-add deploy_key

  git remote set-url origin git@github.com:longhotsummer/za-by-laws.git
  echo git push origin -u master
else
  echo "Ignoring pull request or non-build branch"
  exit 0
fi

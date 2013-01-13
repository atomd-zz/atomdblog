#!/bin/sh
# Push source branch

cd $(dirname "$0")

git checkout -q master
echo ''

[ "$(git status -s)" ] \
    && echo "[ERROR] Not all files are committed. Could not publish the new version of blog." \
    && exit 1

#git add -A
#git commit
#git push origin source

jekyll --no-auto
[ $? -eq 1 ] && echo "[ERROR] Failed to generate site." && exit 1


# Push master branch
git checkout gh-pages
git rm -qr .
cp -r _site/. .
rm -r _site
git add -A
git commit -m "Auto generated at $(date)"

git checkout -q master
git push -f origin gh-pages
echo ''

git push origin master

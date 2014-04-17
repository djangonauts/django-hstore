#!/bin/sh
(cd doc; make)
cp -vr doc/index.html /tmp/index.html;
cp -vr doc/static /tmp/static
cp -vr doc/images /tmp/images
git checkout gh-pages;
rm -rf index.html
rm -rf static
rm -rf images
mv -fv /tmp/images .
mv -fv /tmp/index.html .
mv -fv /tmp/static .
git add --all index.html
git add --all static
git add --all images
git commit -a -m "Update doc"

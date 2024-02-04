#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/PyOMlx.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/PyOMlx.dmg" && rm "dist/PyOMlx.dmg"
create-dmg \
  --volname "PyOMlx" \
  --volicon "logo.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "PyOMlx.app" 175 120 \
  --hide-extension "PyOMlx.app" \
  --app-drop-link 425 120 \
  "dist/PyOMlx.dmg" \
  "dist/dmg/"
## Firefox WhiteSur theme

<p align="center">A MacOS Firefox theme to look more like Big Sur Safari. (For Firefox 70+)</p>

#### Preview
![Preview](preview.png?raw=true)

## Description

Aim is to make Firefox look more like MacOS Big Sur Safari.
This is a CSS theme adapted to work on MacOS from the Linux GTK theme.
Based on https://github.com/vinceliuice/WhiteSur-gtk-theme/tree/master/src/other/firefox
(This is a quick modification, and is not written from scratch.)

## Installation

A script has been added to streamline the installation process.\
Open terminal, and run `bash install.sh`\
Follow the prompts

### Manual installation

Copy `chrome` and `configuration` folers into your Firefox Profile Directory

To find your Firefox Profile Directory you can:

1. Go to `about:support` in Firefox.
2. Application Basics > Profile Directory > Open Directory.
3. Copy folders mentioned above into the profile folder. (usually has `-release` at the end).
4. If you are using Firefox 69+:
	1. Go to `about:config` in Firefox.
	2. Search for `toolkit.legacyUserProfileCustomizations.stylesheets` and set it to `true`.
5. Restart Firefox.
6. Done!


## Known bugs

If it is a fresh install of Firefox, the script's user profile should enable the theme automatically. As a backup, the `pref.js` toggles the setting to enable custom themes.
If for any reason the WhiteSur theme doesn't activate after using the script, follow steps 4.1 and 4.2 to toggle the stylesheets from within the Firefox settings.

The tab background colour is overwritten by themes installed.
e.g. if you are using a dark theme in light mode, tab backgrounds that are inactive are affected.
Fix: Change the installed theme to appropriate colour scheme to avoid issues.

### New bugs

If you've found a new bug, please report it as a new issue with the following:

1. OS you're using
2. Version of Firefox
3. Screenshot of bug if possible
4. Description

Thanks!
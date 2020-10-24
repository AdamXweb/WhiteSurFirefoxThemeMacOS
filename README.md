## Firefox WhiteSur theme

<p align="center">A MacOS Big Sur theme for Firefox 70+</p>

#### Preview
![Preview](preview.png?raw=true)

## Description

This is a CSS theme adapted to work on MacOS from the Linux GTK theme.
Aim is to make Firefox look more like MacOS Big Sur Safari.
Based on https://github.com/vinceliuice/WhiteSur-gtk-theme/tree/master/src/other/firefox
(This is a quick modification, and is not written from scratch.)

## Installation

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

The tab background colour is overwritten by themes installed.
e.g. if you are using a dark theme in light mode, tab backgrounds that are inactive are affected.
Fix: Change the installed theme to appropriate colour scheme to avoid issues.
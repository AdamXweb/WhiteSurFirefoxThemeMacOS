## Firefox WhiteSur theme
<p align="center">
<img width="120" src="https://github.com/a1ex-ak/WhiteSur-MacOS-Firefox-Theme/raw/master/githubpreview/safarifirefox.png?raw=true">
	<br>
A <code>MacOS</code> & <code>Windows</code> Firefox theme to look more like Big Sur Safari. (For Firefox 70+)</p>

![Preview](githubpreview/whitesur.gif?raw=true)

## Description

Aim is to make Firefox look more like MacOS Big Sur Safari.\
This is a CSS theme adapted to work on MacOS from the Linux GTK theme.\
Based on https://github.com/vinceliuice/WhiteSur-firefox-theme \
(This is a quick modification, and is not written from scratch.)

## Installation (MacOS)

Download the [latest release](https://github.com/a1ex-ak/WhiteSur-MacOS-Firefox-Theme/releases/), or clone the repo above.\
A script has been added to streamline the installation process.\
Open terminal in the directory of the repo, and run `bash install.sh`\
Follow the prompts

### Installation flags

The script supports the following flags
- `-c` Left hand side tab close button
- `-w` Left hand side window close button
- `-p` Makes tabs height compact like current Safari
- `-f` To specify the default firefox folder (it will try to find the profile folder to place the theme within)
- `-l` Default location of most Linux installations
- `-u` Remove the animation on URL bar to be clickable throughout
- `-n` Removes the identity colour from tabs
- `-v` Re-enables the tabview button
- `-e` Hides the extension button
- `-s` Single tab view (Tabs hidden when only one tab)
- `-r` Remove the theme

e.g. To install with script, with the tab close button left hand side: `bash install.sh -c` 

#### Optimal experience:
Make sure to right click and Customize Toolbar. From here, drag the new tab button up to the toolbar out of the tab section.

Install with the following modifications for Safari-like experience
` bash ./install.sh -c -n -s -e -p`

This will give you a look like this:
![Preview](https://private-user-images.githubusercontent.com/6800453/391326706-1bb5ffe4-3320-4a8a-8702-648ce3b9f23c.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzMwNTE0OTcsIm5iZiI6MTczMzA1MTE5NywicGF0aCI6Ii82ODAwNDUzLzM5MTMyNjcwNi0xYmI1ZmZlNC0zMzIwLTRhOGEtODcwMi02NDhjZTNiOWYyM2MucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI0MTIwMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNDEyMDFUMTEwNjM3WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MTZjMzgyM2Y0NzMzZmY2NjE5ZmU4MDhiYzc2OGQyYzcwZjE2NWIwNzhmNmM2ZmQ1MTMyZWFhYWI1YzRkNWI0MyZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.4pM0PJgYSjpWUnJRiIYVphkyIMKA1wnGDALqaIHXgk8)

### Manual installation (MacOS & Windows)

Copy `chrome` and `configuration` folders into your Firefox Profile Directory

To find your Firefox Profile Directory you can:

1. Go to `about:support` in Firefox.
2. Application Basics > Profile Directory > Open Directory.
3. Copy folders mentioned above into the profile folder. (usually has `-release` at the end).
4. If you are using Firefox 69+:
	1. Go to `about:config` in Firefox.
	2. Search for `toolkit.legacyUserProfileCustomizations.stylesheets` and set it to `true`.
5. Restart Firefox.
6. Done!

#### Manual theme overrides:
To manually add a custom override, copy the `*.css` from the `custom` folder of whichever option you are after. Place it in the `chrome/WhiteSur/custom` foder within the profile directory you opened above.\

That's it, the theme should load your overriden settings

#### Swap navbar close buttons on Windows:
`windows-swapclose.css` contains the styles required to swap the close buttons, as well as to re-order the close button from MacOS styling to Windows.
Follow the directions above for the manual theme override to activate.
Can be installed with the `-w` command on the install script
#### Swap tab close button side
`tabs-swapclose.css` contains styles to place the close button for the tab on the left hand side for consistency with Safari. Can be installed with the `-c` command on the install script

### Manual colour override:

The theme obeys your system UI colour preferences. If you want to override it e.g. always have the dark theme, then you'll have to do the following.\
The solution if you don't want to change your System UI colour is to do add the following to your `about:config`\
Add: `ui.systemUsesDarkTheme` with the number value with 1 for dark, and 0 for light.\
![Screen Shot 2021-05-04 at 7 10 19 pm](https://user-images.githubusercontent.com/6800453/116982626-60317980-ad0c-11eb-96aa-0879b05c98fc.png)

Please note, you won't be able to change the System UI colour if you are using `privacy.resistFingerprinting`. This apparently is for both web pages and the System UI.

## Known bugs

If it is a fresh install of Firefox, the script for MacOS should enable the settings automatically, however users who have toggled settings may need to do the `about:config` in step 4 above.\
If for any reason the WhiteSur theme doesn't activate after using the script, follow steps 4.1 and 4.2 to toggle the stylesheets from within the Firefox settings.

The tab background colour can be overwritten by themes installed through firefox extentions.
e.g. if you are using a dark theme in light mode, tab backgrounds that are inactive are affected.
Fix: Change the installed theme to appropriate colour scheme to avoid issues.

If you're looking to change the directory to run the script, you can always type `bash` then drag the file into terminal. You can also type `cd` and then drag the folder and press enter to navigate to the directory.\
Alternatively, if you're running Catalina, the default teminal is zsh, meaning you can change folders by typing the name to enter the folder e.g. `WhiteSurFirefoxThemeMacOS`


Q: "Why bother doing this, and not just use safari?" \
A: I've used safari for quite a few years, and was rather disappointed with the change in extensions, particularly with content blocking. This prompted me to use uBlock origin on Firefox, and to customise it to have the best aesthetics, and simplest transition.

### New bugs

If you've found a new bug, please report it as a new issue with the templates provided.

Thanks!

## Screenshots

### Windows
![Preview](githubpreview/whitesurwindows.gif?raw=true)


### MacOS
![Preview](githubpreview/whitesur.gif?raw=true)


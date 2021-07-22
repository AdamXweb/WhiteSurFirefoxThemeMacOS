#! /bin/bash
LHSCLOSE=false
URLBAR=false
REMOVE=false
NOLINE=false
readonly REPO_DIR="$(pwd)"
# readonly REPO_DIR="$(dirname "$(readlink "${0}")")"
source "${REPO_DIR}/lib-install.sh"

# Get options.
while getopts 'c,f:l:u:n,r' flag; do
	case "${flag}" in
        c ) LHSCLOSE=true;;
        f ) FIREFOX_DIR_HOME="${OPTARG}";;
        l ) FIREFOX_DIR_HOME=~/.mozilla/firefox/;;
        u ) URLBAR=true;;
        n) NOLINE=true;;
        r ) REMOVE=true;;
	esac
done

echo -en "$COL_GREEN WhiteSur Firefox theme. $COL_RESET"
echo -en "\n"
echo -en "\n"
echo -e "${bold}WhiteSur installer"
echo -e "⚠ This is a script to add the theme into firefox, and enable it."
echo -e "⚠ Continuing will quit Firefox. Make sure you save any tabs before proceeding."

echo -en "\n"
warn "=> ${bold}$COL_RED CTRL+C $COL_RESET now to abort ${normal} or ${bold} $COL_GREEN ENTER ${normal} $COL_RESET to continue."

tput bel
read -n 1


    actioninfo "Removing Firefox theme..."
    remove_firefox_theme
    success "Done!  Firefox theme has been removed."

# Install Firefox
if [ "$REMOVE" = false ] ; then
    actioninfo "Installing WhiteSur Firefox theme to your directory below"
    install_firefox_theme
    success "Done! WhiteSur Firefox theme has been installed."

    actioninfo "If you have any issues with the theme not activating, follow the two steps below to toggle a setting within Firefox."
    warn "Please go to: ${bold}$COL_RED about:config ${normal} $COL_RESET in Firefox (type it into the URL bar)"
    warn "Search for ${bold}$COL_RED toolkit.legacyUserProfileCustomizations.stylesheets  $COL_RESET and toggle it to `true`"
    actioninfo "That's it, restart Firefox and you're all set!"
fi
echo "Done."
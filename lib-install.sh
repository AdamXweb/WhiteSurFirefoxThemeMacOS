if [[ "${LIB_INSTALL_IMPORTED}" == "true" ]]; then
  echo "ERROR: lib-install.sh is already imported"; exit 1
else LIB_INSTALL_IMPORTED="true"; fi

source "${REPO_DIR}/lib-core.sh"

remove_firefox_theme() {
  killall "firefox" &> /dev/null
  rm -rf "${FIREFOX_DIR_HOME}/"*"default"*"/chrome"
}

install_firefox_theme() {
  remove_firefox_theme
  echo "${FIREFOX_O_HOME}"*"default-release"
  LOC=`echo "${FIREFOX_O_HOME}"*"default-release"`
  cp -rf "${REPO_DIR}/chrome"                                      "${FIREFOX_DIR_HOME}/"*"default-release"
  config_firefox
  echo "Copy complete."
}

config_firefox() {
    cp -rf "${REPO_DIR}/configuration"                             "${FIREFOX_DIR_HOME}/"*"default-release"
# If LeftHandSide close button is wanted, import it in theme.css.
if [ "$LHSCLOSE" = true ] ; then
  cd "${REPO_DIR}"
	echo "Enabling Close button on Left hand side"
      cp -rf "${REPO_DIR}/custom/lhsclose.css"                     "${FIREFOX_DIR_HOME}/"*"default-release/chrome/WhiteSur/parts"
cd "${LOC}"
        sed -i '.bak.css' '17s/^/@import "parts\/lhsclose.css";\
/' chrome/WhiteSur/theme.css
  echo "LSH enabled"
fi
# if no animation on URL bar is desired
if [ "$URLBAR" = true ] ; then
	echo "Removing URL bar animation"
    cd "${REPO_DIR}"
    echo `pwd`
    echo "${REPO_DIR}"
      cp -rf "${REPO_DIR}/custom/standard-urlbar.css"              "${FIREFOX_DIR_HOME}/"*"default-release/chrome/WhiteSur/parts"
cd "${LOC}"
        sed -i '.bak.css' '17s/^/@import "parts\/standard-urlbar.css";\
/' chrome/WhiteSur/theme.css
  echo "Standard URL bar configured"
fi
# if no identity line icon is wanted
if [ "$NOLINE" = true ] ; then
	echo "Removing Facebook / Multi account Identity line"
    cd "${REPO_DIR}"
    echo `pwd`
    echo "${REPO_DIR}"
      cp -rf "${REPO_DIR}/custom/noidentity.css"              "${FIREFOX_DIR_HOME}/"*"default-release/chrome/WhiteSur/parts"
cd "${LOC}"
        sed -i '.bak.css' '17s/^/@import "parts\/noidentity.css";\
/' chrome/WhiteSur/theme.css
  echo "No identity lines configured"
fi
# Copy settings to enable stylesheets in firefox automatically.
  for d in "${FIREFOX_DIR_HOME}/"*"default-release"; do
    echo "user_pref(\"toolkit.legacyUserProfileCustomizations.stylesheets\", true);" >> "${d}/prefs.js"
    echo "user_pref(\"browser.tabs.drawInTitlebar\", true);" >>                         "${d}/prefs.js"
    echo "user_pref(\"browser.uidensity\", 0);" >>                                      "${d}/prefs.js"
    echo "user_pref(\"layers.acceleration.force-enabled\", true);" >>                   "${d}/prefs.js"
    echo "user_pref(\"mozilla.widget.use-argb-visuals\", true);" >>                     "${d}/prefs.js"
  done
}


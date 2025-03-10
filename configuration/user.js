/* user.js
 * https://github.com/rafaelmardojai/firefox-gnome-theme/
 */

// Enable customChrome.css
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Enable CSD
user_pref("browser.tabs.drawInTitlebar", true);

// Set UI density to normal
user_pref("browser.uidensity", 0);

// We remove the inscription "not secure connection", leaving only the icon
user_pref("security.insecure_connection_text.enabled", false);
user_pref("security.insecure_connection_text.pbmode.enabled", false);

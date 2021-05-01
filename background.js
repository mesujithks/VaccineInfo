// this is the background code...
var currentTabId = null;
// listen for our browerAction to be clicked
chrome.browserAction.onClicked.addListener(function (tab) {
  // for the current tab, inject the "inject.js" file & execute it
  if (/cowin.gov.in/.test(tab.url) && currentTabId != tab.id) {
    currentTabId = tab.id;
    chrome.tabs.executeScript(tab.id, {
      file: "inject.js",
    });
  }
});

chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
  // read changeInfo data and do something with it (like read the url)
  if (changeInfo.url) {
    if (/cowin.gov.in/.test(changeInfo.url) && currentTabId != tabId) {
      currentTabId = tabId;
      chrome.tabs.executeScript(tabId, {
        file: "inject.js",
      });
    }
  } else if (/cowin.gov.in/.test(tab.url) && changeInfo.url === undefined) {
    chrome.tabs.executeScript(tabId, { file: "inject.js" });
  }
});

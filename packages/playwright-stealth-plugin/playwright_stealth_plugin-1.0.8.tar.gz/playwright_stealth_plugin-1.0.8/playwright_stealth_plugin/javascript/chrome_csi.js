if (!window.chrome) {
  Object.defineProperty(window, "chrome", {
    writable: true,
    enumerable: true,
    configurable: false,
    value: {},
  });
}

if (
  !("csi" in window.chrome) &&
  (window.performance || window.performance.timing)
) {
  const { csi_timing } = window.performance;

  log.info("loading chrome.csi.js");
  window.chrome.csi = function () {
    return {
      onloadT: csi_timing.domContentLoadedEventEnd,
      startE: csi_timing.navigationStart,
      pageT: Date.now() - csi_timing.navigationStart,
      tran: 15,
    };
  };
  utils.patchToString(window.chrome.csi);
}

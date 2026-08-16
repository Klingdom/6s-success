/**
 * expo-plugin.js — config plugin for the on-device Apple AI module.
 *
 * What it does:
 *   - Ensures the iOS deployment target is high enough to link the module.
 *     (The Foundation Models code itself is @available-guarded, so the app still
 *      runs on older iOS; you just need a recent Xcode/SDK to COMPILE it.)
 *   - Placeholder for a Foundation Models entitlement. None is required today;
 *     if Apple introduces one, add it here via withEntitlementsPlist.
 *
 * Add to app.json / app.config.js:
 *   { "expo": { "plugins": ["./modules/on-device-ai/expo-plugin.js"] } }
 *
 * DIRECTIONAL: verify @expo/config-plugins helpers against your Expo SDK.
 */
const { withPodfileProperties, createRunOncePlugin } = require("@expo/config-plugins");

const PKG = "on-device-ai";
const VERSION = "1.0.0";
const MIN_IOS = "15.1"; // deployment target; FM APIs are guarded above this

const withOnDeviceAI = (config) => {
  config = withPodfileProperties(config, (cfg) => {
    const cur = cfg.modResults["ios.deploymentTarget"];
    if (!cur || parseFloat(cur) < parseFloat(MIN_IOS)) {
      cfg.modResults["ios.deploymentTarget"] = MIN_IOS;
    }
    return cfg;
  });

  // If a future Foundation Models entitlement is required, uncomment and set it:
  //
  // const { withEntitlementsPlist } = require("@expo/config-plugins");
  // config = withEntitlementsPlist(config, (cfg) => {
  //   cfg.modResults["com.apple.developer.foundation-models"] = true;
  //   return cfg;
  // });

  return config;
};

module.exports = createRunOncePlugin(withOnDeviceAI, PKG, VERSION);

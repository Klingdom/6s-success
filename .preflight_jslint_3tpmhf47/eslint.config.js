module.exports = [{
  files: ["**/*.js"],
  languageOptions: {
    ecmaVersion: 2019,
    sourceType: "script",
    globals: {
      window: "writable", document: "readonly", navigator: "readonly",
      location: "readonly", console: "readonly",
      setTimeout: "readonly", setInterval: "readonly",
      clearTimeout: "readonly", clearInterval: "readonly",
      IntersectionObserver: "readonly", MutationObserver: "readonly",
      ResizeObserver: "readonly",
      requestAnimationFrame: "readonly", cancelAnimationFrame: "readonly",
      fetch: "readonly", Promise: "readonly",
      localStorage: "readonly", sessionStorage: "readonly",
      history: "readonly", matchMedia: "readonly", performance: "readonly",
      self: "readonly", caches: "readonly",
      URL: "readonly", URLSearchParams: "readonly", Image: "readonly",
      innerHeight: "readonly", innerWidth: "readonly",
      scrollY: "readonly", scrollX: "readonly",
      addEventListener: "readonly", removeEventListener: "readonly",
      indexedDB: "readonly", Blob: "readonly", FileReader: "readonly",
      CustomEvent: "readonly", Event: "readonly",
      atob: "readonly", btoa: "readonly",
      CATALOG: "readonly", QUEST: "readonly",
      renderProduct: "readonly", observeReveals: "readonly"
    }
  },
  rules: { "no-undef": "error" }
}];

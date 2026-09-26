/* Registered on load rather than immediately, so caching 400 KB of card data
   never competes with painting the page somebody is waiting for. */
if ("serviceWorker" in navigator) {
  addEventListener("load", function () {
    navigator.serviceWorker.register("/sw.js").catch(function () {
      /* No worker means no offline. The app still works, so this is not worth
         interrupting anybody over. */
    });
  });
}
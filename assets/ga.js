// Google Analytics 4 bootstrap. Kept in its own file because the content security policy blocks inline scripts.
(function () {
  var s = document.currentScript, id = s && s.getAttribute("data-id");
  if (!id) return;
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", id);
})();

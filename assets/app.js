// Water Capital Wire page tools: countdown, project calculator, Water Pulse. Loaded as a file because the CSP blocks inline scripts.
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };

  // Countdown on the "coming up" strip
  document.querySelectorAll("[data-start]").forEach(function (el) {
    var d = Math.ceil((new Date(el.getAttribute("data-start") + "T09:00:00+04:00") - new Date()) / 864e5);
    if (d > 1) el.textContent += ", in " + d + " days";
    else if (d === 1) el.textContent += ", tomorrow";
  });

  // Calculator
  if ($("cap")) {
    var U = { m3: { f: 1, l: "m³" }, kgal: { l: "thousand gal" }, bbl: { l: "bbl" } };
    var P = [
      { unit: "m3", cap: 5000, avail: 92, capex: 12, opex: 0.6, val: 1.4, life: 20, rate: 8 },
      { unit: "m3", cap: 100000, avail: 95, capex: 180, opex: 0.45, val: 1.1, life: 25, rate: 7 },
      { unit: "bbl", cap: 40000, avail: 90, capex: 25, opex: 0.25, val: 0.7, life: 10, rate: 10 },
      { unit: "m3", cap: 20000, avail: 98, capex: 30, opex: 0.15, val: 0.3, life: 20, rate: 5 }];
    var keys = ["unit", "cap", "avail", "capex", "opex", "val", "life", "rate"];
    var fm = function (x, d) {
      var a = Math.abs(x), s = x < 0 ? "-" : "";
      if (a >= 1e9) return s + "$" + (a / 1e9).toFixed(2) + "B";
      if (a >= 1e6) return s + "$" + (a / 1e6).toFixed(1) + "M";
      if (a >= 1e3) return s + "$" + (a / 1e3).toFixed(0) + "K";
      return s + "$" + a.toFixed(d === undefined ? 2 : d);
    };
    var cum = [];
    var draw = function () {
      var s = $("cfs"), W = s.clientWidth, H = s.clientHeight;
      if (!W || !cum.length) return;
      var m = { l: W < 520 ? 58 : 66, r: 12, t: 14, b: 26 }, n = cum.length - 1;
      var lo = Math.min.apply(null, [0].concat(cum)), hi = Math.max.apply(null, [0].concat(cum)), sp = (hi - lo) || 1;
      var x = function (i) { return m.l + i * (W - m.l - m.r) / n; };
      var y = function (v) { return m.t + (hi - v) * (H - m.t - m.b) / sp; };
      var pts = cum.map(function (v, i) { return x(i).toFixed(1) + "," + y(v).toFixed(1); });
      var area = "M" + x(0) + "," + y(0) + " L" + pts.join(" L") + " L" + x(n) + "," + y(0) + " Z";
      var step = n > 12 ? (W < 520 ? 10 : 5) : (W < 520 ? 4 : 2), ticks = "";
      for (var i = 0; i <= n; i += step) ticks += '<text x="' + x(i) + '" y="' + (H - 6) + '" text-anchor="middle">' + (i === 0 ? "Year 0" : i) + "</text>";
      s.innerHTML = '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f6fd1" stop-opacity=".45"/><stop offset="1" stop-color="#1f6fd1" stop-opacity=".08"/></linearGradient></defs>' +
        '<path d="' + area + '" fill="url(#g)"/><line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + y(0) + '" y2="' + y(0) + '" stroke="#0f1b2a" stroke-width="1.5"/>' +
        '<polyline points="' + pts.join(" ") + '" fill="none" stroke="#1f6fd1" stroke-width="3"/>' +
        '<text x="' + (m.l - 6) + '" y="' + (y(hi) + 4) + '" text-anchor="end">' + fm(hi, 0) + '</text><text x="' + (m.l - 6) + '" y="' + (y(lo) + 4) + '" text-anchor="end">' + fm(lo, 0) + "</text>" + ticks +
        '<text x="' + (m.l + 8) + '" y="' + (m.t + 10) + '">Cumulative cash, undiscounted</text>';
    };
    var calc = function () {
      var v = {};
      keys.forEach(function (k) { v[k] = k === "unit" ? $(k).value : (parseFloat($(k).value) || 0); });
      var u = U[v.unit];
      document.querySelectorAll(".u").forEach(function (e) { e.textContent = u.l; });
      var vol = v.cap * 365 * v.avail / 100, cap = v.capex * 1e6, r = v.rate / 100, n = Math.max(1, Math.round(v.life));
      var crf = r > 0 ? r * Math.pow(1 + r, n) / (Math.pow(1 + r, n) - 1) : 1 / n;
      var net = (v.val - v.opex) * vol;
      var lcow = vol > 0 ? (cap * crf + v.opex * vol) / vol : 0;
      var npvAt = function (rr) { return -cap + (rr > 0 ? net * (1 - Math.pow(1 + rr, -n)) / rr : net * n); };
      var npv = npvAt(r), irr = null;
      if (net > 0 && npvAt(0) > 0) { var a = 0, b = 5; for (var i = 0; i < 80; i++) { var c = (a + b) / 2; if (npvAt(c) > 0) a = c; else b = c; } irr = (a + b) / 2; }
      $("lcow").textContent = fm(lcow); $("npv").textContent = fm(npv, 0);
      $("pay").textContent = net > 0 ? (cap / net).toFixed(1) + " yrs" : "Never";
      $("irr").textContent = irr === null ? "n/a" : (irr * 100).toFixed(1) + "%";
      cum = []; for (var t = 0; t <= n; t++) cum.push(-cap + net * t);
      draw();
      var gap = v.val - lcow;
      $("verdict").textContent = vol <= 0 ? "Enter a capacity to run the numbers." :
        gap >= 0 ? "Each " + u.l + " costs " + fm(lcow) + " all in and is worth " + fm(v.val) + ", a margin of " + fm(gap) + ". The project clears a " + v.rate + "% hurdle with " + fm(npv, 0) + " of value." :
        "Each " + u.l + " costs " + fm(lcow) + " all in but is worth only " + fm(v.val) + ". The value per unit must rise by " + fm(-gap) + ", or costs fall, before this clears a " + v.rate + "% hurdle.";
    };
    $("presets").addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      document.querySelectorAll("#presets button").forEach(function (x) { x.classList.toggle("on", x === b); });
      var p = P[+b.getAttribute("data-p")]; keys.forEach(function (k) { $(k).value = p[k]; }); calc();
    });
    keys.forEach(function (k) { $(k).addEventListener("input", calc); });
    if (window.ResizeObserver) { var ro = new ResizeObserver(draw); ro.observe($("cf")); }
    calc();
  }

  // Water Pulse self check
  if ($("quiz")) {
    var risk = [[0, 2, 1], [2, 0, 1], [2, 0, 1], [0, 2, 1], [2, 0, 1], [0, 2, 1]];
    var ans = [null, null, null, null, null, null];
    var tiers = [[3, "Ahead of the curve", "You measure, reuse and price water. Your next gain is in supply resilience and contracts.", "#4f8f1f"],
      [7, "Managing it", "You have the basics. Close the gaps in measurement and full cost pricing before a dry year tests them.", "#7a3cc2"],
      [99, "Exposed", "Water is an unpriced operational risk for you. Start with site level metering and a discharge review.", "#c2331f"]];
    $("quiz").addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      var g = b.parentElement, qi = +g.getAttribute("data-q");
      ans[qi] = +b.getAttribute("data-a");
      g.querySelectorAll("button").forEach(function (x) { x.classList.toggle("on", x === b); });
      var done = ans.filter(function (a) { return a !== null; }).length;
      var sc = ans.reduce(function (s, a, i) { return s + (a === null ? 0 : risk[i][a]); }, 0);
      if (done < 6) { $("tier").textContent = done + " of 6 answered"; $("tiertext").textContent = "Keep going for your read."; return; }
      var t = tiers.filter(function (t) { return sc <= t[0]; })[0];
      $("score").style.background = t[3]; $("tier").textContent = t[1];
      $("tiertext").textContent = "Score " + sc + " of 12. " + t[2];
    });
  }

  // Poll: remembered on this device only
  if ($("poll")) {
    var key = "wcw-poll-" + (document.querySelector(".meta") ? document.querySelector(".meta").textContent.slice(0, 20) : "");
    var mark = function (txt) {
      document.querySelectorAll("#poll button").forEach(function (x) { x.classList.toggle("on", x.textContent === txt); });
      $("pollmsg").textContent = "Your pick: " + txt + ". Saved on this device only.";
    };
    try { var saved = localStorage.getItem(key); if (saved) mark(saved); } catch (e) {}
    $("poll").addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      mark(b.textContent);
      try { localStorage.setItem(key, b.textContent); } catch (err) {}
    });
  }

  // Feedback: compose an email, nothing is stored on the site
  if ($("fb")) {
    $("fb").addEventListener("submit", function (e) {
      e.preventDefault();
      var t = $("fbt").value.trim(), to = $("fb").getAttribute("data-mail");
      if (!t) { $("fbmsg").textContent = "Write a topic first."; return; }
      window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent("Water Capital Wire: coverage idea") + "&body=" + encodeURIComponent(t);
      $("fbmsg").textContent = "Your email app should open, addressed to " + to + ". If it does not, write to that address directly.";
    });
  }
})();

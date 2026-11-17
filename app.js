/* ShopList prototype runtime.
 * Renders the design screens in screens.js (built from design/*.dc.html):
 * {{holes}}, <sc-if>, <sc-for>, <dc-import>, onClick handlers and setState.
 */
(function () {
  'use strict';

  var SCREENS = window.SCREENS;
  var FLOWS = [
    { name: 'Discover and onboard', screens: ['SBHome', 'SBIconStates', 'O1Welcome', 'O2Player', 'O3Lists', 'O4Agent', 'V2Seed', 'V2Capture', 'T1Capture', 'T2Shelves', 'T3Agent'] },
    { name: 'Everyday ShopList', screens: ['V2Home', 'V2Refine', 'V2Picks', 'V2Recurring', 'V2Wish'] },
    { name: 'Karma does the legwork', screens: ['V2Agent', 'V2Approve', 'SBStore', 'SBActivate', 'V2Bought'] },
    { name: 'Price Watchlist Update', screens: ['W1Report', 'W2Item', 'W3Schedule', 'W4Notify'] },
    { name: 'Save from any store (extension)', screens: ['ExtPage', 'ExtSave', 'ExtSynced', 'ExtItem'] },
    { name: 'Inside the ShopBack app', screens: ['SBNotifications', 'SBAccount'] },
    { name: 'Inside the ShopBack app', screens: ['SBNotifications', 'SBAccount'] }
  ];
  var ORDER = [];
  FLOWS.forEach(function (f) { f.screens.forEach(function (s) { ORDER.push({ name: s, flow: f.name }); }); });
  var START = 'SBHome';

  /* ---------- component base ---------- */
  function DCLogic(props) { this.props = props || {}; }
  DCLogic.prototype.setState = function (patch) {
    var prev = this.state || {};
    var next = typeof patch === 'function' ? patch(prev) : patch;
    this.state = Object.assign({}, prev, next);
    scheduleRender();
  };
  DCLogic.prototype.forceUpdate = function () { scheduleRender(); };

  var classes = {};
  function getClass(name) {
    if (!classes[name]) {
      classes[name] = new Function('DCLogic', SCREENS[name].script + '\n;return Component;')(DCLogic);
    }
    return classes[name];
  }
  var templates = {};
  function getTemplate(name) {
    if (!templates[name]) {
      var t = document.createElement('template');
      t.innerHTML = SCREENS[name].html;
      templates[name] = t;
    }
    return templates[name];
  }
  function makeComponent(name) {
    var C = getClass(name);
    var inst = new C({});
    return { name: name, inst: inst, children: {} };
  }

  /* ---------- template rendering ---------- */
  var HOLE = /{{\s*([^}]+?)\s*}}/g;
  var WHOLE = /^\s*{{\s*([^}]+?)\s*}}\s*$/;

  function lookup(path, scope) {
    path = path.trim();
    if (path === 'true') return true;
    if (path === 'false') return false;
    if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
    var parts = path.split('.');
    var v = Object.prototype.hasOwnProperty.call(scope.locals, parts[0]) ? scope.locals[parts[0]] : (scope.vals || {})[parts[0]];
    for (var i = 1; i < parts.length; i++) {
      if (v == null) return undefined;
      v = v[parts[i]];
    }
    return v;
  }
  function interp(str, scope) {
    return str.replace(HOLE, function (_, p) { var v = lookup(p, scope); return v == null ? '' : String(v); });
  }
  function wholeValue(attr, scope) {
    var m = WHOLE.exec(attr || '');
    return m ? lookup(m[1], scope) : undefined;
  }

  function renderNodes(nodes, scope, parent, ctx) {
    for (var i = 0; i < nodes.length; i++) renderNode(nodes[i], scope, parent, ctx);
  }

  function renderNode(n, scope, parent, ctx) {
    if (n.nodeType === 3) { parent.appendChild(document.createTextNode(interp(n.nodeValue, scope))); return; }
    if (n.nodeType !== 1) return;
    var tag = n.localName;

    if (tag === 'sc-if') {
      if (wholeValue(n.getAttribute('value'), scope)) renderNodes(n.childNodes, scope, parent, ctx);
      return;
    }
    if (tag === 'sc-for') {
      var list = wholeValue(n.getAttribute('list'), scope) || [];
      var as = n.getAttribute('as') || 'item';
      list.forEach(function (item, idx) {
        var locals = Object.assign({}, scope.locals);
        locals[as] = item;
        locals.$index = idx;
        renderNodes(n.childNodes, { vals: scope.vals, locals: locals }, parent, ctx);
      });
      return;
    }
    if (tag === 'dc-import') {
      var name = n.getAttribute('name');
      ctx.counter[name] = (ctx.counter[name] || 0) + 1;
      var key = name + '#' + ctx.counter[name];
      var child = ctx.owner.children[key];
      if (!child) {
        child = makeComponent(name);
        ctx.owner.children[key] = child;
        if (child.inst.componentDidMount) setTimeout(function () { child.inst.componentDidMount(); });
      }
      var wrap = document.createElement('div');
      wrap.className = 'dc-import';
      renderComponent(child, wrap);
      parent.appendChild(wrap);
      return;
    }

    var el = document.createElementNS(n.namespaceURI, n.localName);
    for (var i = 0; i < n.attributes.length; i++) {
      var a = n.attributes[i];
      var an = a.name;
      if (an.indexOf('hint-') === 0) continue;
      if (/^on[a-z]+$/i.test(an)) {
        var fn = wholeValue(a.value, scope);
        if (typeof fn === 'function') el.addEventListener(an.slice(2).toLowerCase(), (function (f) { return function (e) { f(e); }; })(fn));
        continue;
      }
      var v = interp(a.value, scope);
      if (an === 'href') {
        if (/\.dc\.html$/.test(v)) {
          v = '#/' + v.replace(/^.*\//, '').replace('.dc.html', '');
        } else if (/^https?:/.test(v)) {
          el.setAttribute('target', '_blank');
          el.setAttribute('rel', 'noopener');
        } else if (v === '#') {
          el.addEventListener('click', function (e) { e.preventDefault(); });
        }
      }
      el.setAttribute(an, v);
    }
    renderNodes(n.childNodes, scope, el, ctx);
    parent.appendChild(el);
  }

  function renderComponent(c, container) {
    var vals = c.inst.renderVals ? c.inst.renderVals() : {};
    var ctx = { owner: c, counter: {} };
    renderNodes(getTemplate(c.name).content.childNodes, { vals: vals, locals: {} }, container, ctx);
  }

  function unmount(c) {
    if (!c) return;
    Object.keys(c.children).forEach(function (k) { unmount(c.children[k]); });
    if (c.inst.componentWillUnmount) c.inst.componentWillUnmount();
  }

  /* ---------- app shell ---------- */
  var root = null;
  var pending = false;
  var stage = document.getElementById('stage');
  var screenEl = null;

  function scheduleRender() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(function () { pending = false; renderRoot(); });
  }

  function renderRoot() {
    if (!root || !screenEl) return;
    var scroller = screenEl.parentNode;
    var top = scroller.scrollTop;
    var active = document.activeElement;
    var focusId = active && screenEl.contains(active) ? active.id : '';
    var caret = focusId && typeof active.selectionStart === 'number' ? active.selectionStart : null;
    var scrolls = [];
    screenEl.querySelectorAll('[id]').forEach(function (el) {
      if (el.scrollLeft || el.scrollTop) scrolls.push([el.id, el.scrollLeft, el.scrollTop]);
    });
    screenEl.textContent = '';
    renderComponent(root, screenEl);
    scroller.scrollTop = top;
    scrolls.forEach(function (sc) {
      var el = document.getElementById(sc[0]);
      if (el) { el.scrollLeft = sc[1]; el.scrollTop = sc[2]; }
    });
    if (focusId) {
      var again = document.getElementById(focusId);
      if (again) {
        again.focus();
        if (caret !== null) { try { again.setSelectionRange(caret, caret); } catch (err) { /* not a text field */ } }
      }
    }
  }

  function cleanTitle(t) {
    return t.replace(/^[A-Z]?\d*\s*·\s*/, '').replace(/\s*\((press|switch)[^)]*\)/, '');
  }

  function current() {
    var name = decodeURIComponent((location.hash || '').replace(/^#\/?/, ''));
    return SCREENS[name] ? name : START;
  }

  function layout() {
    var s = SCREENS[root.name];
    var device = stage.firstChild;
    if (!device) return;
    var isPhone = s.w === 390;
    var viewH = isPhone ? Math.min(s.h, 844) : s.h;
    var availW = stage.clientWidth - 32;
    var availH = window.innerHeight - stage.getBoundingClientRect().top - 24;
    var scale = Math.min(1, availW / s.w);
    if (isPhone) scale = Math.min(scale, Math.max(availH / viewH, 0.62));
    var frame = device.firstChild;
    frame.style.transform = 'scale(' + scale + ')';
    device.style.width = (s.w * scale) + 'px';
    device.style.height = (viewH * scale) + 'px';
  }

  function show() {
    var name = current();
    unmount(root);
    root = makeComponent(name);
    var s = SCREENS[name];
    var isPhone = s.w === 390;

    stage.textContent = '';
    var device = document.createElement('div');
    device.className = 'device';
    var frame = document.createElement('div');
    frame.className = 'frame ' + (isPhone ? 'phone' : s.w === 1280 ? 'desktop' : 'panel');
    frame.style.width = s.w + 'px';
    frame.style.height = (isPhone ? Math.min(s.h, 844) : s.h) + 'px';
    screenEl = document.createElement('div');
    screenEl.className = 'screen';
    frame.appendChild(screenEl);
    device.appendChild(frame);
    stage.appendChild(device);

    renderComponent(root, screenEl);
    if (root.inst.componentDidMount) root.inst.componentDidMount();
    layout();

    var idx = ORDER.findIndex(function (o) { return o.name === name; });
    document.getElementById('title').textContent = cleanTitle(s.title);
    document.getElementById('flow').textContent = idx >= 0 ? ORDER[idx].flow + ' · ' + (idx + 1) + ' of ' + ORDER.length : '';
    document.title = cleanTitle(s.title) + ' · ShopList prototype';
    var prev = document.getElementById('prev');
    var next = document.getElementById('next');
    prev.disabled = idx <= 0;
    next.disabled = idx < 0 || idx >= ORDER.length - 1;
    prev.onclick = function () { if (idx > 0) location.hash = '#/' + ORDER[idx - 1].name; };
    next.onclick = function () { if (idx < ORDER.length - 1) location.hash = '#/' + ORDER[idx + 1].name; };

    document.querySelectorAll('#nav a').forEach(function (a) {
      a.setAttribute('aria-current', a.getAttribute('data-name') === name ? 'page' : 'false');
    });
    var sel = document.getElementById('jump');
    if (sel) sel.value = name;
  }

  function buildNav() {
    var nav = document.getElementById('nav');
    var sel = document.getElementById('jump');
    FLOWS.forEach(function (f) {
      var h = document.createElement('h2');
      h.textContent = f.name;
      nav.appendChild(h);
      var og = document.createElement('optgroup');
      og.label = f.name;
      f.screens.forEach(function (s) {
        var label = cleanTitle(SCREENS[s].title);
        var a = document.createElement('a');
        a.href = '#/' + s;
        a.setAttribute('data-name', s);
        a.textContent = label;
        nav.appendChild(a);
        var o = document.createElement('option');
        o.value = s;
        o.textContent = label;
        og.appendChild(o);
      });
      sel.appendChild(og);
    });
    sel.addEventListener('change', function () { location.hash = '#/' + sel.value; });
  }

  document.addEventListener('keydown', function (e) {
    var t = e.target.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT') return;
    if (e.key === 'ArrowRight') document.getElementById('next').click();
    if (e.key === 'ArrowLeft') document.getElementById('prev').click();
  });

  buildNav();
  window.addEventListener('hashchange', show);
  window.addEventListener('resize', function () { if (root) layout(); });
  show();
})();

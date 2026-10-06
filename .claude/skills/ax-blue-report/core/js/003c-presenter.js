(function() {
 var d = document, body = d.body, SCRIPT = function() {
  var o = {};
  Array.prototype.forEach.call(document.querySelectorAll('#deck > section.sl'), function(el) {
   var t = el.getAttribute('data-t');
   if (t) {
    o[t] = {
     a: '',
     c: '',
     t: el.getAttribute('data-notes') || ''
    };
   }
  });
  return o;
 }();
 var laser = d.createElement('div');
 laser.id = 'laser';
 body.appendChild(laser);
 var panel = d.createElement('div');
 panel.id = 'scr';
 body.appendChild(panel);
 var win = null, t0 = null, tick = null, state = {
  el: null,
  cur: 0,
  list: [],
  step: 0,
  steps: 0
 };
 var LSKEY = 'axbr.script.' + (document.title || 'deck');
 var ORIG = {};
 (function() {
  for (var k in SCRIPT) {
   ORIG[k] = SCRIPT[k].t;
  }
 })();
 var edited = {}, editing = false, editKey = '', lastTotal = '';
 function allSl() {
  return Array.prototype.slice.call(d.querySelectorAll('.sl'));
 }
 function spokenLen(t) {
  var ls = String(t || '').split('\n').filter(function(l) {
   return l.trim().indexOf('※') !== 0;
  });
  return ls.join('\n').split('[클릭]').join('').replace(/\s/g, '').length;
 }
 function mm(n) {
  return Math.floor(n / 60) + ':' + ('0' + n % 60).slice(-2);
 }
 function estOf(t) {
  return mm(Math.max(20, Math.ceil(spokenLen(t) / 300 * 60 / 5) * 5));
 }
 function retime() {
  var cum = 0, list = allSl();
  list.forEach(function(el) {
   var k = el.dataset.t, sc = SCRIPT[k];
   if (!sc) {
    return;
   }
   if (el.classList.contains('apx')) {
    return;
   }
   var a = el.classList.contains('div') ? '0:05' : estOf(sc.t);
   var p = a.split(':');
   cum += parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
   sc.a = a;
   sc.c = mm(cum);
  });
  var total = mm(cum);
  list.forEach(function(el) {
   var sc = SCRIPT[el.dataset.t];
   if (sc && el.classList.contains('apx')) {
    sc.a = '0:00';
    sc.c = total;
   }
  });
  lastTotal = total;
  return total;
 }
 function applyNotes() {
  allSl().forEach(function(el) {
   var sc = SCRIPT[el.dataset.t];
   if (sc) {
    el.setAttribute('data-notes', sc.t);
   }
  });
  try {
   var nx = d.getElementById('ntx');
   if (nx && state.el) {
    nx.textContent = state.el.getAttribute('data-notes') || '';
   }
  } catch (e) {}
 }
 function saveLS() {
  try {
   var o = {}, n = 0;
   for (var k in edited) {
    if (edited[k] && SCRIPT[k]) {
     o[k] = SCRIPT[k].t;
     n++;
    }
   }
   if (n) {
    localStorage.setItem(LSKEY, JSON.stringify(o));
   } else {
    localStorage.removeItem(LSKEY);
   }
  } catch (e) {}
 }
 function loadLS() {
  try {
   var raw = localStorage.getItem(LSKEY);
   if (!raw) {
    return 0;
   }
   var o = JSON.parse(raw), n = 0;
   for (var k in o) {
    if (SCRIPT[k] && typeof o[k] === 'string') {
     SCRIPT[k].t = o[k];
     edited[k] = true;
     n++;
    }
   }
   if (n) {
    retime();
    applyNotes();
   }
   return n;
  } catch (e) {
   return 0;
  }
 }
 function editCount() {
  var n = 0;
  for (var k in edited) {
   if (edited[k]) {
    n++;
   }
  }
  return n;
 }
 function stamp() {
  var z = new Date, p = function(x) {
   return ('0' + x).slice(-2);
  };
  return z.getFullYear() + p(z.getMonth() + 1) + p(z.getDate()) + '_' + p(z.getHours()) + p(z.getMinutes());
 }
 var DLCAP;
 function dlcap() {
  if (DLCAP !== undefined) {
   return Promise.resolve(DLCAP);
  }
  try {
   if (window.claude && typeof window.claude.use === 'function') {
    return window.claude.use('downloads').then(function(x) {
     DLCAP = x || null;
     return DLCAP;
    }, function() {
     DLCAP = null;
     return null;
    });
   }
  } catch (e) {}
  DLCAP = null;
  return Promise.resolve(null);
 }
 function showRaw(name, text) {
  var ov = d.getElementById('rawdl');
  if (ov) {
   ov.remove();
  }
  ov = d.createElement('div');
  ov.id = 'rawdl';
  ov.style.cssText = 'position:fixed;inset:6vh 8vw;z-index:9600;display:flex;flex-direction:column;gap:10px;padding:16px;border-radius:10px;background:#0d1326;color:#e8ecf6;box-shadow:0 20px 60px rgba(0,0,0,.5)';
  var h = d.createElement('div');
  h.style.cssText = 'display:flex;align-items:center;gap:10px;font:800 14px/1.3 var(--kr)';
  h.innerHTML = '<span>' + name + '</span>';
  var bc = d.createElement('button');
  bc.textContent = '전체 선택 후 복사(Ctrl+C)';
  bc.style.cssText = 'margin-left:auto;font:700 12px/1 var(--kr);padding:7px 11px;border-radius:5px;border:1px solid #3c4a70;background:#1a2340;color:#c7d2ea;cursor:pointer';
  var bx = d.createElement('button');
  bx.textContent = '닫기';
  bx.style.cssText = bc.style.cssText;
  h.appendChild(bc);
  h.appendChild(bx);
  var ta = d.createElement('textarea');
  ta.readOnly = true;
  ta.value = text;
  ta.style.cssText = 'flex:1;min-height:0;width:100%;resize:none;background:#0a0f1e;color:#e8ecf6;border:1px solid #3c4a70;border-radius:6px;padding:12px;font:500 13px/1.6 Pretendard,-apple-system,sans-serif;outline:none';
  ov.appendChild(h);
  ov.appendChild(ta);
  d.body.appendChild(ov);
  function sel() {
   try {
    ta.focus();
    ta.select();
   } catch (e) {}
  }
  bc.addEventListener('click', function(e) {
   e.stopPropagation();
   sel();
  });
  bx.addEventListener('click', function(e) {
   e.stopPropagation();
   ov.remove();
  });
  ta.addEventListener('keydown', function(e) {
   e.stopPropagation();
   if (e.key === 'Escape') {
    ov.remove();
   }
  });
  sel();
 }
 function copyOut(name, text) {
  try {
   if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function() {
     toast('클립보드에 복사했습니다 · 붙여넣어 쓰십시오');
    }, function() {
     showRaw(name, text);
    });
    return;
   }
  } catch (e) {}
  showRaw(name, text);
 }
 function dl(name, text, mime) {
  dlcap().then(function(cap) {
   if (cap && cap.save) {
    cap.save({
     filename: name,
     data: text
    }).then(function() {
     toast('내려받았습니다 · ' + name);
    }, function(err) {
     var c = err && err.code;
     if (c === 'declined') {
      return;
     }
     copyOut(name, text);
    });
    return;
   }
   try {
    var b = new Blob([ '\ufeff' + text ], {
     type: (mime || 'text/plain') + ';charset=utf-8'
    });
    var u = URL.createObjectURL(b);
    var a = d.createElement('a');
    a.href = u;
    a.download = name;
    d.body.appendChild(a);
    a.click();
    setTimeout(function() {
     try {
      URL.revokeObjectURL(u);
      a.remove();
     } catch (e) {}
    }, 800);
    setTimeout(function() {
     if (!DLCAP) {
      toast('내려받기가 막히면 「복사」 버튼을 쓰십시오');
     }
    }, 900);
   } catch (e) {
    copyOut(name, text);
   }
  });
 }
 function copyEdits() {
  var o = {}, n = 0;
  for (var k in edited) {
   if (edited[k] && SCRIPT[k]) {
    o[k] = SCRIPT[k].t;
    n++;
   }
  }
  if (!n) {
   toast('수정한 장이 없습니다');
   return;
  }
  copyOut('AX_대본_수정.json', JSON.stringify(o, null, 2));
 }
 function exportEdits() {
  var o = {}, n = 0;
  for (var k in edited) {
   if (edited[k] && SCRIPT[k]) {
    o[k] = SCRIPT[k].t;
    n++;
   }
  }
  if (!n) {
   toast('수정한 장이 없습니다');
   return;
  }
  dl('AX_대본_수정_' + stamp() + '.json', JSON.stringify(o, null, 2), 'application/json');
  toast(n + '개 장 내보냄 · 이 파일을 주시면 덱에 반영합니다');
 }
 function exportAll() {
  var out = [ '# ' + (document.title || '덱') + ' · 발표 대본', '총 ' + (lastTotal || retime()) + ' · 내보낸 시각 ' + stamp(), '' ];
  allSl().forEach(function(el) {
   var k = el.dataset.t, sc = SCRIPT[k];
   if (!sc) {
    return;
   }
   out.push('## ' + k + '  [' + (sc.a || '-') + ' · 누적 ' + (sc.c || '-') + ']' + (edited[k] ? '  (수정됨)' : ''), '', sc.t, '');
  });
  dl('AX_대본_전체_' + stamp() + '.md', out.join('\n'), 'text/markdown');
  toast('전체 대본을 내려받았습니다');
 }
 function resetAll() {
  if (!editCount()) {
   toast('수정한 장이 없습니다');
   return;
  }
  for (var k in edited) {
   if (edited[k] && SCRIPT[k] && ORIG[k] !== undefined) {
    SCRIPT[k].t = ORIG[k];
   }
  }
  edited = {};
  retime();
  applyNotes();
  saveLS();
  editing = false;
  paint(true);
  toast('모두 원본으로 되돌렸습니다');
 }
 var RULES = [ [ 'html,body', 'margin:0;height:100%;background:#0d1326;color:#e8ecf6;font:500 17px/1.65 Pretendard,"Malgun Gothic",system-ui,sans-serif' ], [ '*', 'box-sizing:border-box' ], [ '.top', 'display:flex;align-items:baseline;gap:14px;padding:14px 20px 10px;border-bottom:1px solid rgba(255,255,255,.12)' ], [ '.top .n', 'font:800 30px/1 Pretendard,-apple-system,"Malgun Gothic",sans-serif;font-variant-numeric:tabular-nums;color:#8fb6f6' ], [ '.top .t', 'font:800 22px/1.2 inherit;flex:1;color:#fff' ], [ '.top .tm', 'font:700 15px/1 Pretendard,-apple-system,"Malgun Gothic",sans-serif;font-variant-numeric:tabular-nums;color:#c7d2ea;text-align:right;white-space:nowrap' ], [ '.top .tm b', 'display:block;font-size:26px;color:#fff;margin-bottom:4px;cursor:pointer' ], [ '.top .tm b.late', 'color:#ff7b7b' ], [ '.top .tm b.early', 'color:#7ee0a3' ], [ '.st', 'padding:6px 20px;font:700 13px/1 Pretendard,-apple-system,"Malgun Gothic",sans-serif;color:#8fb6f6;letter-spacing:.06em;border-bottom:1px solid rgba(255,255,255,.08)' ], [ '.bd', 'flex:1;overflow:auto;padding:16px 20px 20px;font-size:19px;line-height:1.7;margin:0;display:block' ], [ '.bd p', 'margin:0 0 .9em' ], [ '.bd strong', 'color:#fff' ], [ '.k', 'display:inline-block;font:800 12px/1 Pretendard,-apple-system,"Malgun Gothic",sans-serif;padding:4px 8px;border-radius:5px;background:#2f4a9c;color:#fff;margin:0 6px 0 0;vertical-align:2px;letter-spacing:.04em' ], [ '.k.done', 'background:#1f7a4d' ], [ '.k.now', 'background:#ff8c00;box-shadow:0 0 0 3px rgba(255,140,0,.35)' ], [ '.tr', 'margin-top:14px;padding:12px 14px;border-left:4px solid #8fb6f6;background:rgba(143,182,246,.1);font-size:17px' ], [ '.tr b', 'color:#8fb6f6' ], [ '.nx', 'padding:12px 20px;border-top:1px solid rgba(255,255,255,.12);font-size:15px;color:#c7d2ea' ], [ '.nx b', 'color:#fff' ], [ '.ft', 'padding:8px 20px 12px;font-size:12px;line-height:1.6;color:#7f8db0;border-top:1px solid rgba(255,255,255,.08)' ], [ '.ft b', 'color:#c7d2ea' ], [ 'kbd', 'font:inherit;padding:1px 5px;border:1px solid #556;border-radius:4px' ], [ '.memo', 'margin:0 0 .9em;padding:8px 12px;border-left:3px solid #4a577d;background:rgba(255,255,255,.04);color:#9aa7c6;font-size:16px;line-height:1.6' ], [ '.st', 'display:flex;align-items:center;gap:10px' ], [ '.ebadge', 'flex:0 0 auto;font:800 11px/1 Pretendard,-apple-system,"Malgun Gothic",sans-serif;padding:4px 7px;border-radius:4px;background:#ff8c00;color:#141a2c;letter-spacing:0' ], [ '.eop', 'margin-left:auto;display:flex;gap:6px;flex-wrap:wrap' ], [ '.eop button', 'font:700 12px/1 Pretendard,-apple-system,"Malgun Gothic",sans-serif;padding:6px 10px;border-radius:5px;border:1px solid #3c4a70;background:#1a2340;color:#c7d2ea;cursor:pointer;letter-spacing:0' ], [ '.eop button:hover', 'border-color:#8fb6f6;color:#fff' ], [ '.eop button[data-ed="save"]', 'background:#2f4a9c;border-color:#2f4a9c;color:#fff' ], [ '.eop button[data-ed="reset"]', 'border-color:#7a3b3b;color:#ffb3b3' ], [ '.bd.ed', 'display:flex;flex-direction:column;gap:8px;padding:12px 20px 16px;overflow:hidden' ], [ '.bd.ed textarea', 'flex:1 1 auto;min-height:0;width:100%;resize:none;background:#0a0f1e;color:#e8ecf6;border:1px solid #3c4a70;border-radius:6px;padding:12px 14px;font:500 16px/1.75 Pretendard,-apple-system,"Malgun Gothic",sans-serif;outline:none;white-space:pre-wrap' ], [ '.bd.ed textarea:focus', 'border-color:#8fb6f6;box-shadow:0 0 0 3px rgba(143,182,246,.18)' ], [ '.edm', 'flex:0 0 auto;display:flex;gap:12px;flex-wrap:wrap;align-items:baseline;font:700 12px/1.5 Pretendard,-apple-system,"Malgun Gothic",sans-serif;color:#8fb6f6' ], [ '.edm em', 'font-style:normal;font-weight:500;color:#7f8db0' ] ];
 function cssFor(prefix) {
  return RULES.map(function(r) {
   if (prefix && (r[0] === 'html,body' || r[0] === '*')) {
    return '';
   }
   return r[0].split(',').map(function(sel) {
    return prefix ? prefix + ' ' + sel : sel;
   }).join(',') + '{' + r[1] + '}';
  }).join('');
 }
 var CSS = cssFor('');
 var st = d.createElement('style');
 st.textContent = cssFor('#scr') + '#scr .top .n{font-size:22px}#scr .top .t{font-size:17px;border:0;padding:0;white-space:normal;letter-spacing:0;vertical-align:baseline}#scr .bd{font-size:16px;position:static}';
 d.head.appendChild(st);
 function fontCss() {
  var out = '';
  try {
   Array.prototype.forEach.call(d.styleSheets, function(sh) {
    try {
     Array.prototype.forEach.call(sh.cssRules, function(r) {
      if (r.type === CSSRule.FONT_FACE_RULE) {
       out += r.cssText;
      }
     });
    } catch (e) {}
   });
  } catch (e) {}
  return out;
 }
 function esc(x) {
  return x.replace(/&/g, '&amp;').replace(/</g, '&lt;');
 }
 function fmt(sec) {
  sec = Math.max(0, Math.round(sec));
  return Math.floor(sec / 60) + ':' + ('0' + sec % 60).slice(-2);
 }
 function toSec(t) {
  var p = t.split(':');
  return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
 }
 function md(t, step) {
  var k = 0, html = esc(t).replace(/\*\*\[클릭\]\*\*/g, function() {
   k++;
   var c = k <= step ? 'done' : k === step + 1 ? 'now' : '';
   return '<span class="k ' + c + '">클릭 ' + k + '</span>';
  }).replace(/\[클릭\]/g, function() {
   k++;
   var c = k <= step ? 'done' : k === step + 1 ? 'now' : '';
   return '<span class="k ' + c + '">클릭 ' + k + '</span>';
  }).replace(/\*\*\[넘김\]\*\*/g, '<span class="k">넘김</span>').replace(/\*\*\[([^\]]+)\]\*\*/g, '<span class="k">$1</span>').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  return html.split(/\n\s*\n/).map(function(pg) {
   pg = pg.trim();
   if (!pg) {
    return '';
   }
   if (pg.indexOf('→ 전환:') === 0) {
    return '<div class="tr"><b>전환</b> ' + pg.slice(5).trim() + '</div>';
   }
   if (pg.indexOf('※') === 0) {
    return '<div class="memo">' + pg.replace(/\n/g, '<br>') + '</div>';
   }
   return '<p>' + pg.replace(/\n/g, '<br>') + '</p>';
  }).join('');
 }
 function render() {
  var el = state.el;
  if (!el) {
   return '';
  }
  var t = el.dataset.t || '', sc = SCRIPT[t], nxt = state.list[state.cur + 1], nt = nxt ? nxt.dataset.t || '' : '(끝)';
  var isDiv = el.classList.contains('div');
  if (isDiv && !sc) {
   var n2 = state.list[state.cur + 1];
   sc = {
    a: '0:10',
    c: '',
    t: '간지. 넘기면서 한 마디만.\n\n→ 전환: ' + (n2 ? '다음 장 「' + (n2.dataset.t || '') + '」으로. ' : '') + '**[넘김]**'
   };
  }
  if (!sc) {
   sc = {
    a: '',
    c: '',
    t: '(이 장의 대본 없음 · 발표자 메모: ' + (el.getAttribute('data-notes') || '') + ')'
   };
  }
  var num = t.split(' ')[0], name = t.slice(num.length).trim();
  if (!/^[A-Z0-9①-⑩]/.test(num)) {
   num = '';
   name = t;
  }
  var ela = t0 ? (Date.now() - t0) / 1e3 : 0, cls = '', diff = '';
  if (sc.c && t0) {
   var plan = toSec(sc.c) - toSec(sc.a || '0:00');
   var dv = ela - plan;
   cls = dv > 45 ? 'late' : dv < -45 ? 'early' : '';
   diff = (dv >= 0 ? '+' : '−') + fmt(Math.abs(dv)) + ' vs 이 장 시작 예정 ' + fmt(plan);
  }
  var stepTxt = state.steps ? '단계 ' + state.step + ' / ' + state.steps : '단계 없음';
  var isEd = editing && editKey === t, ec = editCount();
  var badge = edited[t] ? '<span class="ebadge">수정됨</span>' : '';
  var ops = isEd ? '<button data-ed="save" title="Ctrl+Enter">저장</button><button data-ed="cancel" title="Esc">취소</button><button data-ed="revert">이 장 원본</button>' : '<button data-ed="edit" title="이 장 대본 고치기">✎ 편집</button><button data-ed="exp">내보내기' + (ec ? ' (' + ec + ')' : '') + '</button><button data-ed="copy" title="수정분을 클립보드로">복사</button><button data-ed="expall">전체</button>' + (ec ? '<button data-ed="reset">전부 원복</button>' : '');
  var bodyHtml = isEd ? '<div class="bd ed"><textarea id="edta" spellcheck="false"></textarea><div class="edm"><span id="edc">–</span><em>Ctrl+Enter 저장 · Esc 취소 · [클릭] 은 화면 한 단계를 뜻합니다 · ※ 로 시작하는 줄은 읽지 않는 메모</em></div></div>' : '<div class="bd">' + md(sc.t, state.step) + '</div>';
  return '<div class="top"><span class="n">' + esc(num) + '</span><span class="t">' + esc(name || t) + '</span><span class="tm"><b class="' + cls + '" title="클릭하면 0:00부터" onclick="window.__rst&&window.__rst()">' + fmt(ela) + '</b>배정 ' + esc(sc.a || '–') + ' · 누적 ' + esc(sc.c || '–') + (diff ? '<br>' + esc(diff) : '') + '</span></div>' + '<div class="st">' + stepTxt + badge + '<span class="eop">' + ops + '</span></div>' + bodyHtml + '<div class="nx">다음 · <b>' + esc(nt) + '</b>' + (nxt && SCRIPT[nxt.dataset.t] ? ' · 배정 ' + esc(SCRIPT[nxt.dataset.t].a) : '') + '</div>' + '<div class="ft"><kbd>→</kbd> <kbd>Space</kbd> 다음 · <kbd>←</kbd> 이전 · <kbd>PgDn</kbd> <kbd>PgUp</kbd> 장 이동 · 이 창에서 눌러도 됩니다 · 타이머는 발표 모드 진입 때 0:00<br><b>✎ 편집</b>으로 이 장 대본을 바로 고칩니다 · 저장하면 이 브라우저에 남고 배정·누적 시간이 다시 계산됩니다 · <b>내보내기</b>(파일) 또는 <b>복사</b>(클립보드)로 받은 내용을 주시면 덱에 영구 반영합니다' + (lastTotal ? ' · 현재 총 ' + lastTotal : '') + '</div>';
 }
 function measure(ta, box) {
  if (!ta || !box) {
   return;
  }
  var v = ta.value;
  box.textContent = spokenLen(v) + '자(읽는 분량) · 예상 ' + estOf(v) + ' · 전체 ' + v.length + '자';
 }
 function wire(rootEl) {
  if (!rootEl) {
   return;
  }
  Array.prototype.forEach.call(rootEl.querySelectorAll('[data-ed]'), function(b) {
   b.addEventListener('click', function(ev) {
    ev.preventDefault();
    ev.stopPropagation();
    act(b.getAttribute('data-ed'), rootEl);
   });
  });
  var ta = rootEl.querySelector('#edta');
  if (ta) {
   var key = editKey, cur = SCRIPT[key] && SCRIPT[key].t || '';
   ta.value = draft !== null && draft !== undefined ? draft : cur;
   var box = rootEl.querySelector('#edc');
   measure(ta, box);
   ta.addEventListener('input', function() {
    draft = ta.value;
    measure(ta, box);
   });
   ta.addEventListener('keydown', function(ev) {
    ev.stopPropagation();
    if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') {
     ev.preventDefault();
     act('save', rootEl);
    } else if (ev.key === 'Escape') {
     ev.preventDefault();
     act('cancel', rootEl);
    }
   });
   try {
    ta.focus();
    ta.setSelectionRange(ta.value.length, ta.value.length);
   } catch (e) {}
  }
 }
 var draft = null;
 function act(cmd, rootEl) {
  if (cmd === 'edit') {
   editKey = state.el && state.el.dataset.t || '';
   if (!editKey) {
    return;
   }
   draft = SCRIPT[editKey] && SCRIPT[editKey].t || '';
   editing = true;
   paint(true);
   return;
  }
  if (cmd === 'cancel') {
   editing = false;
   draft = null;
   paint(true);
   return;
  }
  if (cmd === 'save') {
   var ta = rootEl && rootEl.querySelector('#edta');
   var v = ta ? ta.value : draft;
   if (v === null || v === undefined) {
    v = '';
   }
   if (!SCRIPT[editKey]) {
    SCRIPT[editKey] = {
     a: '',
     c: '',
     t: ''
    };
   }
   SCRIPT[editKey].t = v;
   if (v === ORIG[editKey]) {
    delete edited[editKey];
   } else {
    edited[editKey] = true;
   }
   retime();
   applyNotes();
   saveLS();
   editing = false;
   draft = null;
   paint(true);
   toast('저장했습니다 · 총 ' + lastTotal);
   return;
  }
  if (cmd === 'revert') {
   var k = editKey || (state.el && state.el.dataset.t || '');
   if (!k || ORIG[k] === undefined) {
    return;
   }
   draft = ORIG[k];
   var ta2 = rootEl && rootEl.querySelector('#edta');
   if (ta2) {
    ta2.value = ORIG[k];
    measure(ta2, rootEl.querySelector('#edc'));
    try {
     ta2.focus();
    } catch (e) {}
   }
   toast('이 장 원본을 불러왔습니다 · 저장을 눌러야 적용됩니다');
   return;
  }
  if (cmd === 'exp') {
   exportEdits();
   return;
  }
  if (cmd === 'copy') {
   copyEdits();
   return;
  }
  if (cmd === 'expall') {
   exportAll();
   return;
  }
  if (cmd === 'reset') {
   resetAll();
   return;
  }
 }
 var lastKey = '';
 function put(host, h, changed) {
  var ob = host.querySelector('.bd'), s1 = ob ? ob.scrollTop : 0, s0 = host.scrollTop;
  host.innerHTML = h;
  wire(host);
  if (editing) {
   return;
  }
  var bd = host.querySelector('.bd'), now = host.querySelector('.k.now');
  if (changed) {
   if (now && bd) {
    now.scrollIntoView({
     block: 'center'
    });
   } else if (bd) {
    bd.scrollTop = 0;
   }
  } else {
   if (bd) {
    bd.scrollTop = s1;
   }
   host.scrollTop = s0;
  }
 }
 function paint(force) {
  if (editing && !force) {
   return;
  }
  var h = render(), key = (state.el && state.el.dataset.t || '') + '|' + state.step, changed = key !== lastKey;
  lastKey = key;
  if (win && !win.closed) {
   try {
    var b = win.document.getElementById('root');
    if (b) {
     put(b, h, changed);
    }
   } catch (e) {}
  }
  if (body.classList.contains('scr')) {
   put(panel, '<div id="proot" style="display:flex;flex-direction:column;height:100%">' + h + '</div>', changed);
  }
 }
 function tickPaint() {
  var m = render().match(/<span class="tm">([\s\S]*?)<\/span><\/div>/);
  if (!m) {
   return;
  }
  function upd(host) {
   var tm = host && host.querySelector('.tm');
   if (tm) {
    tm.innerHTML = m[1];
   }
  }
  if (win && !win.closed) {
   try {
    upd(win.document.getElementById('root'));
   } catch (e) {}
  }
  if (body.classList.contains('scr')) {
   upd(panel);
  }
 }
 function openWin() {
  try {
   win = window.open('', 'ax_presenter', 'width=720,height=900,menubar=no,toolbar=no,location=no,status=no');
  } catch (e) {
   win = null;
  }
  if (!win) {
   body.classList.add('scr');
   paint();
   toast('새 창이 막혀 화면 안 패널로 엽니다 · P로 닫기');
   return false;
  }
  try {
   var doc = win.document;
   if (!doc.getElementById('root')) {
    doc.open();
    doc.write('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>대본 · '+(document.title||'')+'</title><style>' + fontCss() + CSS + '</style></head><body><div id="root" style="display:flex;flex-direction:column;height:100%"></div></body></html>');
    doc.close();
    win.addEventListener('keydown', function(e) {
     var tg = e.target;
     if (tg && (tg.tagName === 'TEXTAREA' || tg.tagName === 'INPUT' || tg.isContentEditable)) {
      return;
     }
     var k = e.key;
     if ([ 'ArrowRight', ' ', 'ArrowLeft', 'PageDown', 'PageUp', 'ArrowDown', 'ArrowUp', 'Home', 'End' ].indexOf(k) >= 0) {
      e.preventDefault();
      window.dispatchEvent(new KeyboardEvent('keydown', {
       key: k
      }));
     }
    });
    win.__rst = function() {
     t0 = Date.now();
     paint();
    };
   }
   win.focus();
   paint();
   return true;
  } catch (e) {
   body.classList.add('scr');
   paint();
   return false;
  }
 }
 function closeWin() {
  if (win && !win.closed) {
   try {
    win.close();
   } catch (e) {}
  }
  win = null;
  body.classList.remove('scr');
 }
 function toast(msg) {
  var t = d.createElement('div');
  t.textContent = msg;
  t.style.cssText = 'position:fixed;left:50%;bottom:6vh;transform:translateX(-50%);background:#0d1326;color:#fff;padding:.7rem 1.1rem;border-radius:.5rem;font:600 1rem/1 var(--kr);z-index:9500;opacity:.95';
  body.appendChild(t);
  setTimeout(function() {
   t.remove();
  }, 2600);
 }
 window.__rst = function() {
  t0 = Date.now();
  paint();
 };
 d.addEventListener('deck:sync', function(e) {
  var newKey = e.detail && e.detail.el && e.detail.el.dataset.t || '';
  if (editing && newKey !== editKey) {
   if (draft !== null && draft !== undefined && SCRIPT[editKey] && draft !== SCRIPT[editKey].t) {
    SCRIPT[editKey].t = draft;
    if (draft === ORIG[editKey]) {
     delete edited[editKey];
    } else {
     edited[editKey] = true;
    }
    retime();
    applyNotes();
    saveLS();
    toast('편집 중이던 「' + editKey + '」을 저장했습니다');
   }
   editing = false;
   draft = null;
  }
  state = e.detail;
  paint(true);
 });
 (function() {
  var n = loadLS();
  retime();
  if (n) {
   setTimeout(function() {
    toast('이전에 저장한 대본 수정 ' + n + '개 장을 불러왔습니다');
   }, 900);
  }
 })();
 d.addEventListener('deck:presenter', function() {
  if (win && !win.closed) {
   closeWin();
  } else if (body.classList.contains('scr')) {
   body.classList.remove('scr');
  } else {
   openWin();
  }
 });
 d.addEventListener('deck:present', function(e) {
  if (e.detail.on) {
   t0 = Date.now();
   body.classList.add('laser');
   laserPlace();
   laser.classList.add('on');
   openWin();
   if (tick) {
    clearInterval(tick);
   }
   tick = setInterval(tickPaint, 1e3);
  } else {
   closeWin();
   body.classList.remove('laser');
   laser.classList.remove('on');
   if (tick) {
    clearInterval(tick);
   }
   tick = null;
  }
 });
 var lt;
 d.addEventListener('deck:laser', function() {
  body.classList.toggle('laser');
  if (!body.classList.contains('laser')) {
   laser.classList.remove('on');
  }
 });
 var lx = innerWidth / 2, ly = innerHeight / 2;
 function laserPlace() {
  laser.style.transform = 'translate(' + lx + 'px,' + ly + 'px)';
 }
 addEventListener('mousemove', function(e) {
  lx = e.clientX;
  ly = e.clientY;
  if (!body.classList.contains('present') || !body.classList.contains('laser')) {
   return;
  }
  laserPlace();
  laser.classList.add('on');
 }, {
  passive: true
 });
 addEventListener('mouseout', function(e) {
  if (!e.relatedTarget && !e.toElement) {
   laser.classList.remove('on');
  }
 }, {
  passive: true
 });
 addEventListener('blur', function() {
  laser.classList.remove('on');
 });
 addEventListener('beforeunload', function() {
  closeWin();
 });
})();

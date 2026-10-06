(function() {
 var root = document.getElementById('apx-stack-picker');
 if (!root) {
  return;
 }
 var D = JSON.parse(root.querySelector('.k8-data').textContent), chart = root.querySelector('.k8-chart'), rows = root.querySelector('.k8-rows'), axis = root.querySelector('.k8-axis'), leg = root.querySelector('.k8-leg'), tip = root.querySelector('.k8-tip'), pick = root.querySelector('.k8-pick'), est = root.querySelector('.k8-est');
 var DEF = [ 'cpa', 'cpb', 'cpc', 'cpd', 'own', 'cpe' ];
 var S = {
  mode: 'rel',
  view: 'nat',
  sel: DEF.slice()
 };
 var CAT = {
  p: [ '인건비', '#2f4a9c' ],
  o: [ '외주 · 재료 · 구매', '#d9a45b' ],
  d: [ '감가상각', '#a8620a' ],
  x: [ '기타 영업비용', '#9aa3b5' ],
  s: [ '일회성 · 손상', '#b33a3a' ],
  u: [ '비용 · 성격 미구분', '#c9ced9' ],
  c: [ '매출원가', '#4b5f9e' ],
  sell: [ '판매비', '#e0a458' ],
  adm: [ '관리비', '#8fa0cf' ],
  sga: [ '판매·관리비', '#7c86ad' ],
  rd: [ '연구개발비', '#6a3fa0' ]
 };
 var OPN = [ '영업이익', '#157a4a' ], GN = {
  g: '글로벌',
  h: '국내 상장',
  k: '중견 · 국내 교정'
 };
 function krw(c, v) {
  return v * c.fx / 100;
 }
 function fmt(n) {
  n = Math.round(n);
  return n.toLocaleString('ko-KR');
 }
 function fmtB(e) {
  if (!e) {
   return '0';
  }
  return e >= 1e4 ? (e / 1e4).toFixed(e >= 1e5 ? 1 : 2) + '조' : fmt(e) + '억';
 }
 function on(id) {
  return S.sel.indexOf(id) >= 0;
 }
 function cos() {
  return D.co.filter(function(c) {
   return !c.seg;
  });
 }
 function byId(id) {
  return D.co.filter(function(x) {
   return x.id === id;
  })[0];
 }
 function pct(c) {
  return c.mg != null ? c.mg : Math.round(c.oi / c.rev * 1e3) / 10;
 }
 function list() {
  return D.co.filter(function(c) {
   return on(c.id) && (S.view === 'nat' || c.fn);
  });
 }
 function segs(c) {
  return S.view === 'nat' ? c.nat : c.fn;
 }
 function buildPick() {
  var h = '<span class="k8-pl">비교 회사</span>';
  [ 'g', 'h', 'k' ].forEach(function(g) {
   h += '<span class="k8-pg"><button type="button" class="k8-gb" data-g="' + g + '" title="' + GN[g] + ' 모두 켜기 · 끄기">' + GN[g] + '</button>';
   D.co.forEach(function(c) {
    if (c.grp === g) {
     h += '<button type="button" class="k8-cb' + (c.seg ? ' k8-sub' : '') + '" data-id="' + c.id + '" aria-pressed="false"' + (c.seg ? ' title="샘플테크 부문 막대 추가 · 상세 분석은 부록 17"' : '') + '>' + (c.pick || c.name.replace(' (연결)', '')) + '</button>';
    }
   });
   h += '</span>';
  });
  h += '<span class="k8-cnt"></span><button type="button" class="k8-rs">기본 6사</button><button type="button" class="k8-all">전체</button>';
  pick.innerHTML = h;
 }
 function syncPick() {
  [].forEach.call(pick.querySelectorAll('.k8-cb'), function(b) {
   var id = b.getAttribute('data-id'), c = D.co.filter(function(x) {
    return x.id === id;
   })[0];
   b.setAttribute('aria-pressed', on(id));
   b.classList.toggle('nofn', S.view === 'fn' && !c.fn);
   b.title = S.view === 'fn' && !c.fn ? c.seg ? '부문별 기능별 비용 미공시' : '기능별 비용 미공시' : c.seg ? '샘플테크 부문 막대 추가 · 상세 분석은 부록 17' : '';
  });
  var L = list(), nc = L.filter(function(c) {
   return !c.seg;
  }).length, ns = L.filter(function(c) {
   return c.seg;
  }).length, lbl = nc + '곳' + (ns ? ' + 부문 ' + ns : ' 표시');
  pick.querySelector('.k8-cnt').textContent = S.view === 'fn' && L.length !== S.sel.length ? lbl + '(선택 ' + S.sel.length + ' · 기능별 공시만)' : lbl;
  if (est) {
   est.hidden = !on('cpe');
  }
 }
 function render() {
  var L = list(), n = L.length, max = 0;
  var ks = n ? Math.min(2.8, Math.max(1, Math.pow(13 / n, .8))) : 1, kf = 1 + (ks - 1) * .45;
  chart.style.setProperty('--ks', ks.toFixed(3));
  chart.style.setProperty('--kf', kf.toFixed(3));
  syncPick();
  if (!n) {
   axis.innerHTML = '';
   rows.innerHTML = '<p class="k8-empty">선택한 회사 중 기능별 비용을 공시한 곳이 없습니다<br>성격별로 보거나 회사를 더 고르세요</p>';
   leg.innerHTML = '';
   return;
  }
  L.forEach(function(c) {
   var tot = segs(c).reduce(function(a, s) {
    return a + s[1];
   }, 0), top = Math.max(c.rev, tot);
   max = Math.max(max, S.mode === 'rel' ? top / c.rev * 100 : krw(c, top));
  });
  if (S.mode === 'rel') {
   max = Math.max(110, Math.ceil(max / 10) * 10);
  } else {
   var st = max > 5e4 ? 2e4 : max > 1e4 ? 5e3 : max > 2e3 ? 500 : 100;
   max = Math.ceil(max / st) * st;
  }
  var n2 = S.mode === 'rel' ? [ 0, 20, 40, 60, 80, 100 ].concat(max > 110 ? [ max ] : []) : [ 0, .25, .5, .75, 1 ].map(function(f) {
   return f * max;
  });
  axis.innerHTML = '<span class="lb"></span><div class="sc">' + n2.map(function(v) {
   return '<i style="left:' + v / max * 100 + '%"><b>' + (S.mode === 'rel' ? v : fmtB(v)) + '</b></i>';
  }).join('') + (S.mode === 'rel' ? '<i class="h100" style="left:' + 100 / max * 100 + '%"></i>' : '') + '</div><span class="rt">영업이익</span>';
  var bw = (axis.querySelector('.sc') || {}).offsetWidth || 0;
  if (bw < 200) {
   bw = 1100;
  }
  var rf = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16, fp = .78 * kf * rf;
  function fits(w, t) {
   var em = 0;
   String(t).split('').forEach(function(ch) {
    em += /[\uac00-\ud7a3]/.test(ch) ? 1 : .62;
   });
   return w / 100 * bw > em * fp + fp * .9;
  }
  rows.innerHTML = L.map(function(c, ri) {
   var h = '', k = S.mode === 'rel' ? 100 / c.rev : c.fx / 100;
   segs(c).forEach(function(s, si) {
    var w = s[1] * k / max * 100;
    var cat = CAT[s[0]];
    h += '<i class="sg' + (s[2] ? ' est' : '') + '" data-c="' + s[0] + '" data-v="' + s[1] + '" style="width:' + w + '%;background:' + cat[1] + ';--d:' + (ri * 40 + si * 60) + 'ms">' + function() {
     var t = (S.mode === 'rel' ? Math.round(s[1] / c.rev * 100) : fmtB(krw(c, s[1]))) + (s[2] ? ' 추정' : '');
     return fits(w, t) ? '<em>' + t + '</em>' : '';
    }() + '</i>';
   });
   var oi = c.oi, ow = Math.abs(oi) * k / max * 100;
   if (oi >= 0) {
    h += '<i class="sg op" data-c="op" data-v="' + oi + '" style="width:' + ow + '%;--d:' + (ri * 40 + 400) + 'ms">' + function() {
     var t = S.mode === 'rel' ? Math.round(oi / c.rev * 100) : fmtB(krw(c, oi));
     return fits(ow, t) ? '<em>' + t + '</em>' : '';
    }() + '</i>';
   }
   var rl = c.rev * k / max * 100;
   var ls = oi < 0 ? '<b class="ls" style="left:' + rl + '%;width:' + ow + '%">손실</b>' : '';
   var mg = pct(c).toFixed(1);
   return '<div class="rw ' + c.grp + (c.seg ? ' seg' : '') + '" data-id="' + c.id + '"><div class="lb"><b>' + c.name + '</b><small>' + (c.sub ? c.sub : c.cc + ' · ' + c.cur) + ' · 매출 ' + fmtB(krw(c, c.rev)) + '</small></div><div class="br">' + h + ls + '<u class="rv" style="left:' + rl + '%"></u></div><div class="rt' + (oi < 0 ? ' neg' : '') + '"><b>' + mg + '%</b><small>' + (S.mode === 'abs' ? fmtB(krw(c, oi)) : c.adj || '공시 영업이익') + '</small></div></div>';
  }).join('');
  var used = {};
  L.forEach(function(c) {
   segs(c).forEach(function(s) {
    used[s[0]] = 1;
   });
  });
  leg.innerHTML = Object.keys(CAT).filter(function(k) {
   return used[k];
  }).map(function(k) {
   return '<span><i style="background:' + CAT[k][1] + '"></i>' + CAT[k][0] + '</span>';
  }).join('') + '<span><i style="background:' + OPN[1] + '"></i>영업이익</span><span><u></u>매출선</span>';
  chart.classList.toggle('abs', S.mode === 'abs');
  var g = 0;
  while (rows.clientHeight > 0 && rows.scrollHeight > rows.clientHeight + 1 && ks > .56 && g++ < 18) {
   ks -= .04;
   kf = 1 + (ks - 1) * .45;
   chart.style.setProperty('--ks', ks.toFixed(3));
   chart.style.setProperty('--kf', kf.toFixed(3));
  }
 }
 root.addEventListener('click', function(e) {
  var b = e.target.closest('.k8-seg button');
  if (!b) {
   return;
  }
  e.stopPropagation();
  var g = b.parentNode, k = g.getAttribute('data-k');
  S[k] = b.getAttribute('data-v');
  [].forEach.call(g.children, function(x) {
   x.setAttribute('aria-pressed', x === b);
  });
  render();
 }, true);
 pick.addEventListener('click', function(e) {
  var b = e.target.closest('button');
  if (!b) {
   return;
  }
  e.stopPropagation();
  e.preventDefault();
  if (b.classList.contains('k8-cb')) {
   var id = b.getAttribute('data-id');
   if (on(id)) {
    if (S.sel.length > 1) {
     S.sel.splice(S.sel.indexOf(id), 1);
    }
   } else {
    S.sel.push(id);
   }
  } else if (b.classList.contains('k8-gb')) {
   var g = b.getAttribute('data-g'), ids = cos().filter(function(c) {
    return c.grp === g;
   }).map(function(c) {
    return c.id;
   }), all = ids.every(on);
   if (all) {
    var rest = S.sel.filter(function(x) {
     return ids.indexOf(x) < 0;
    });
    if (rest.length) {
     S.sel = rest;
    }
   } else {
    ids.forEach(function(x) {
     if (!on(x)) {
      S.sel.push(x);
     }
    });
   }
  } else if (b.classList.contains('k8-rs')) {
   S.sel = DEF.slice();
  } else if (b.classList.contains('k8-all')) {
   S.sel = cos().map(function(c) {
    return c.id;
   }).concat(S.sel.filter(function(id) {
    var c = byId(id);
    return c && c.seg;
   }));
  }
  render();
 }, true);
 rows.addEventListener('mousemove', function(e) {
  var sg = e.target.closest('.sg'), rw = e.target.closest('.rw');
  if (!sg || !rw) {
   tip.hidden = true;
   return;
  }
  var c = D.co.filter(function(x) {
   return x.id === rw.getAttribute('data-id');
  })[0], key = sg.getAttribute('data-c'), v = +sg.getAttribute('data-v');
  var nm = (key === 'op' ? '영업이익' : CAT[key][0]) + (sg.classList.contains('est') ? ' (추정)' : '');
  tip.innerHTML = '<b>' + c.name + ' · ' + nm + '</b><span>' + v.toLocaleString('en-US', {
   maximumFractionDigits: 1
  }) + ' 백만 ' + c.cur + ' → ' + fmtB(krw(c, v)) + ' 원</span><span>매출 대비 ' + (v / c.rev * 100).toFixed(1) + '%</span><small>' + c.src + '</small><small>' + c.note + '</small>';
  var r = root.querySelector('.bd').getBoundingClientRect(), s = r.width / root.querySelector('.bd').offsetWidth || 1;
  tip.style.left = (e.clientX - r.left) / s + 14 + 'px';
  tip.style.top = (e.clientY - r.top) / s + 14 + 'px';
  tip.hidden = false;
 });
 rows.addEventListener('mouseleave', function() {
  tip.hidden = true;
 });
 buildPick();
 render();
})();

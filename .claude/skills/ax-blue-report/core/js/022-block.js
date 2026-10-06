(function() {
 var root = document.getElementById('flow-pipeline');
 if (!root) {
  return;
 }
 var stage = root.querySelector('.tz-stage'), well = root.querySelector('.tz-well'), scanl = root.querySelector('.tz-scanl'), gates = [].slice.call(root.querySelectorAll('.tz-gate')), bin = root.querySelector('.tz-bin');
 var core = root.querySelector('.tz-core'), fit = root.querySelector('.tz-fit'), cmp = root.querySelector('.tz-cmp'), pt = root.querySelector('.tz-pt'), kb = root.querySelector('.tz-kb'), kn = root.querySelector('.tz-kn');
 var rcs = [].slice.call(root.querySelectorAll('.tz-rc')), list = root.querySelector('.tz-list'), arc = root.querySelector('.tz-arcp2'), arcsvg = root.querySelector('.tz-arc');
 var CAT = [ 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9' ], WT = [ 12, 9, 14, 12, 13, 9, 10, 11, 10 ];
 var TITLES = [ [ '배터리 안전성 시험', 1 ], [ 'EMC 적합성 시험', 1 ], [ '환경 신뢰성 시험', 1 ], [ '국내 인증 대행', 2 ], [ '제품 인증 심사', 2 ], [ '시험법 표준화 용역', 3 ], [ '규격 개발 용역', 3 ], [ '시험 설비 운영 용역', 0 ], [ '성능 평가 시험', 0 ] ];
 var PTS = [ '보유 규격 경험 강조', '납기 대응력 제시', '유사 수주 실적 인용', '공동 제안 검토' ];
 var CMPS = [ '예상 2개사', '예상 3개사', '경쟁 적음', '경쟁 치열' ];
 var run = false, scanning = false, tms = [], COLS = 10, ROWS = 9, heights = [], cell = 0, know = 0, seq = 0;
 function later(ms, fn) {
  tms.push(setTimeout(function() {
   if (run) {
    fn();
   }
  }, ms));
 }
 function rel(el) {
  var r = el.getBoundingClientRect(), p = stage.getBoundingClientRect();
  return {
   l: r.left - p.left,
   t: r.top - p.top,
   w: r.width,
   h: r.height,
   cx: r.left - p.left + r.width / 2,
   cy: r.top - p.top + r.height / 2
  };
 }
 function pickCat() {
  var s = 0, i;
  for (i = 0; i < WT.length; i++) {
   s += WT[i];
  }
  var r = Math.random() * s;
  for (i = 0; i < WT.length; i++) {
   r -= WT[i];
   if (r < 0) {
    return CAT[i];
   }
  }
  return 'c9';
 }
 function blocks() {
  return [].slice.call(well.querySelectorAll('.tz-blk'));
 }
 function resetWell() {
  heights = [];
  for (var i = 0; i < COLS; i++) {
   heights.push(0);
  }
  blocks().forEach(function(b) {
   b.remove();
  });
  well.classList.remove('scan');
  cell = well.clientWidth / COLS;
 }
 function drop() {
  if (!run) {
   return;
  }
  if (scanning) {
   later(300, drop);
   return;
  }
  var n = ROWS * COLS, placed = 0;
  for (var q = 0; q < n; q++) {
   var c = pickCat();
   var base = ROWS, col = 0, i;
   for (i = 0; i < COLS; i++) {
    if (heights[i] < base) {
     base = heights[i];
     col = i;
    }
   }
   if (base >= ROWS) {
    break;
   }
   var span = 1;
   while (col + span < COLS && heights[col + span] === base && span < 4) {
    span++;
   }
   var w = Math.min(span, 1 + Math.floor(Math.random() * 4));
   var h = Math.random() < .3 && base + 2 <= ROWS ? 2 : 1;
   var b = document.createElement('i');
   b.className = 'tz-blk ' + c;
   b.style.width = cell * w - 2 + 'px';
   b.style.height = cell * h - 2 + 'px';
   b.style.left = col * cell + 1 + 'px';
   b.style.top = -cell * h - (ROWS - base) * cell * .4 + 'px';
   well.appendChild(b);
   void b.offsetWidth;
   b.style.top = well.clientHeight - (base + h) * cell + 1 + 'px';
   for (var i2 = col; i2 < col + w; i2++) {
    heights[i2] = base + h;
   }
   placed++;
  }
  later(placed ? 900 + Math.random() * 300 : 400, drop);
 }
 function tok(cls, x, y) {
  var t = document.createElement('i');
  t.className = 'tz-tk ' + cls;
  t.style.left = x + 'px';
  t.style.top = y + 'px';
  stage.appendChild(t);
  void t.offsetWidth;
  return t;
 }
 function mv(t, x, y) {
  t.style.left = x + 'px';
  t.style.top = y + 'px';
 }
 function type(el, text, ms, cb) {
  el.textContent = '';
  var i = 0;
  (function tick() {
   if (!run) {
    return;
   }
   el.textContent = text.slice(0, ++i);
   if (i < text.length) {
    tms.push(setTimeout(tick, ms));
   } else if (cb) {
    cb();
   }
  })();
 }
 function cycle() {
  if (!run) {
   return;
  }
  var my = ++seq;
  scanning = true;
  var bl = blocks();
  if (bl.length && !bl.some(function(b) {
   return b.classList.contains('c1');
  })) {
   bl[bl.length - 1].className = 'tz-blk c1';
  }
  well.classList.add('scan');
  scanl.hidden = false;
  later(520, function() {
   if (my !== seq) {
    return;
   }
   var hits = [], near = null;
   blocks().forEach(function(b) {
    if (b.classList.contains('c1')) {
     b.classList.add('hit');
     hits.push(b);
    } else if (!near && b.classList.contains('c2') && Math.random() < .4) {
     near = b;
     b.classList.add('hit');
    } else {
     b.classList.add('dim');
    }
   });
   var c = near && know > 0 && Math.random() < .5 ? 'c2' : 'c1';
   later(480, function() {
    if (my !== seq) {
     return;
    }
    var g0 = rel(gates[0]);
    var tx = g0.l - 16, ty = g0.cy - 7;
    var lead = null;
    var srcs = hits.concat(near ? [ near ] : []);
    if (!srcs.length) {
     var w = rel(well);
     lead = tok('c1', w.cx - 8, w.cy - 7);
     c = 'c1';
     later(40, function() {
      mv(lead, tx, ty);
     });
    }
    srcs.forEach(function(b) {
     var r = rel(b);
     var isC2 = b.classList.contains('c2');
     var t = tok(isC2 ? 'c2' : 'c1', r.l + r.w / 2 - 8, r.t + r.h / 2 - 7);
     b.style.opacity = '0';
     var isLead = c === 'c2' ? b === near : b === hits[0];
     later(40, function() {
      mv(t, tx, ty);
     });
     if (isLead) {
      lead = t;
     } else {
      later(400, function() {
       t.style.opacity = '0';
       later(200, function() {
        t.remove();
       });
      });
     }
    });
    well.classList.remove('scan');
    scanl.hidden = true;
    well.classList.add('clr');
    later(320, function() {
     well.classList.remove('clr');
     resetWell();
     scanning = false;
    });
    later(450, function() {
     if (my !== seq) {
      return;
     }
     gatesRun(my, c, lead);
    });
   });
  });
 }
 function gatesRun(my, c, t) {
  gates.forEach(function(g) {
   g.classList.remove('ok', 'ng');
  });
  var fails = [];
  if (c === 'c2') {
   fails = [ 0 ];
  } else if (know > 0 && Math.random() < .3) {
   fails = [ Math.random() < .5 ? 1 : 2 ];
  }
  var d = 0;
  gates.forEach(function(g, i) {
   later(d += 330, function() {
    if (my !== seq) {
     return;
    }
    var r = rel(g);
    mv(t, r.l + r.w - 22, r.cy - 7);
   });
   later(d += 200, function() {
    if (my !== seq) {
     return;
    }
    if (fails.length && fails[0] < i) {
     return;
    }
    if (fails.length && fails[0] === i) {
     g.classList.add('ng');
     var bb = rel(bin);
     later(200, function() {
      mv(t, bb.cx - 8, bb.cy - 7);
      t.style.opacity = '0';
      later(300, function() {
       t.remove();
      });
     });
    } else {
     g.classList.add('ok');
    }
   });
  });
  var passed = !fails.length;
  var pick = TITLES[Math.floor(Math.random() * TITLES.length)];
  later(d += 250, function() {
   if (my !== seq) {
    return;
   }
   if (!passed) {
    later(350, cycle);
    return;
   }
   var cr = rel(core);
   mv(t, cr.cx - 8, cr.cy - 7);
   t.style.opacity = '0';
   core.classList.add('think');
   later(350, function() {
    t.remove();
    fit.textContent = '·····';
    cmp.textContent = '';
    pt.textContent = '';
    var f = Math.min(5, 3 + Math.floor(know / 3) + (Math.random() < .5 ? 1 : 0));
    var i = 0;
    (function fill() {
     if (!run) {
      return;
     }
     i++;
     fit.textContent = '●'.repeat(i) + '○'.repeat(5 - i);
     if (i < f) {
      tms.push(setTimeout(fill, 90));
     } else {
      type(cmp, CMPS[Math.floor(Math.random() * 4)], 22, function() {
       type(pt, PTS[Math.floor(Math.random() * 4)] + (know >= 3 ? ' · 과거 결과 반영' : ''), 20, function() {
        core.classList.remove('think');
        deliver(pick, f);
       });
      });
     }
    })();
   });
  });
 }
 function deliver(pick, f) {
  if (!run) {
   return;
  }
  var card = rel(root.querySelector('.tz-card'));
  var m = tok('mail', card.l + card.w - 14, card.t + 10);
  var rc = rcs[pick[1]];
  var r = rel(rc);
  later(60, function() {
   mv(m, r.l + r.w - 26, r.cy - 7);
  });
  later(350, function() {
   rc.classList.add('hot');
  });
  later(800, function() {
   var l = rel(list);
   mv(m, l.l + 8, l.t + 4);
   m.style.opacity = '0';
   later(350, function() {
    m.remove();
    rc.classList.remove('hot');
    manage(pick, f);
   });
  });
 }
 function manage(pick, f) {
  if (!run) {
   return;
  }
  var it = document.createElement('div');
  it.className = 'tz-it';
  it.innerHTML = '<i style="background:var(--c1)"></i><span>' + pick[0] + '</span><em>검토</em>';
  list.insertBefore(it, list.firstChild);
  while (list.children.length > 4) {
   list.removeChild(list.lastChild);
  }
  var em = it.querySelector('em');
  var bid = Math.random() < .75;
  later(600, function() {
   em.textContent = bid ? '응찰' : '미응찰';
   em.className = bid ? 's1' : 's3';
  });
  later(1200, function() {
   if (bid) {
    var win = Math.random() < .5;
    em.textContent = win ? '수주' : '미수주';
    em.className = win ? 's2' : 's3';
   }
   feedback(em.textContent, em.className);
  });
  later(300, cycle);
 }
 function feedback(lab, cls) {
  if (!run) {
   return;
  }
  var l = rel(list), a = rel(arcsvg);
  var t = tok('rec ' + (cls || ''), l.l + l.w * .9, l.t - 2);
  t.textContent = lab || '결과';
  arcsvg.classList.add('flow');
  var L = arc.getTotalLength();
  var t0 = performance.now();
  (function step() {
   if (!run || !t.parentNode) {
    return;
   }
   var p = Math.min(1, (performance.now() - t0) / 900);
   var pt2 = arc.getPointAtLength(L * p);
   var sx = a.w / 1e3, sy = a.h / 60;
   t.style.left = a.l + pt2.x * sx - 7 + 'px';
   t.style.top = a.t + pt2.y * sy - 7 + 'px';
   if (p < 1) {
    requestAnimationFrame(step);
   } else {
    t.remove();
    arcsvg.classList.remove('flow');
    know++;
    kn.textContent = know;
    kb.style.width = Math.min(100, 6 + know * 9) + '%';
    core.style.setProperty('--lv', Math.min(know, 5));
    core.classList.add('learn');
    var lb = root.querySelector('.tz-lv');
    if (lb) {
     lb.textContent = '학습 ' + know + '회 · 더 정확해짐';
     lb.classList.add('pop');
    }
    later(900, function() {
     core.classList.remove('learn');
     if (lb) {
      lb.classList.remove('pop');
     }
    });
   }
  })();
 }
 function seed() {
  list.innerHTML = '';
  [ [ 'EMC 적합성 시험', 's2', '수주' ], [ '국내 인증 대행', 's1', '응찰' ], [ '시험법 표준화 용역', 's3', '미응찰' ] ].forEach(function(x) {
   var it = document.createElement('div');
   it.className = 'tz-it';
   it.innerHTML = '<i style="background:var(--c1)"></i><span>' + x[0] + '</span><em class="' + x[1] + '">' + x[2] + '</em>';
   list.appendChild(it);
  });
 }
 function start() {
  if (run) {
   return;
  }
  run = true;
  scanning = false;
  know = 0;
  kn.textContent = '0';
  kb.style.width = '6%';
  core.style.setProperty('--lv', 0);
  var lb0 = root.querySelector('.tz-lv');
  if (lb0) {
   lb0.textContent = '실행 결과가 돌아올수록';
  }
  resetWell();
  seed();
  drop();
  later(3800, cycle);
 }
 function stop() {
  run = false;
  arcsvg.classList.remove('flow');
  core.classList.remove('learn');
  scanning = false;
  tms.forEach(clearTimeout);
  tms = [];
  seq++;
  [].slice.call(stage.querySelectorAll('.tz-tk')).forEach(function(e) {
   e.remove();
  });
  well.classList.remove('scan', 'clr');
  scanl.hidden = true;
  core.classList.remove('think');
  gates.forEach(function(g) {
   g.classList.remove('ok', 'ng');
  });
  rcs.forEach(function(r) {
   r.classList.remove('hot');
  });
 }
 var io = new IntersectionObserver(function(es) {
  es.forEach(function(e) {
   if (e.intersectionRatio >= .55) {
    start();
   } else {
    stop();
   }
  });
 }, {
  threshold: [ .55 ]
 });
 io.observe(root);
 window.addEventListener('resize', function() {
  if (run) {
   stop();
   start();
  }
 });
})();

(function() {
 if (!window.EventTarget || !EventTarget.prototype || !EventTarget.prototype.addEventListener) {
  return;
 }
 var orig = EventTarget.prototype.addEventListener;
 EventTarget.prototype.addEventListener = function(type, fn, opt) {
  try {
   if (type === 'click' && this && this.nodeType === 1 && this.setAttribute && this.closest) {
    var sl = this.closest('.sl');
    if (sl && this !== sl && !this.classList.contains('wrap') && !this.classList.contains('bd')) {
     this.setAttribute('data-int', '1');
    }
   }
  } catch (e) {}
  return orig.call(this, type, fn, opt);
 };
})();

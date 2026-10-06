(() => {
 const scene = document.querySelector('#apx-hub-scenes');
 if (!scene) {
  return;
 }
 new IntersectionObserver(es => es.forEach(e => e.target.classList.toggle('v46-inview', e.isIntersecting)), {
  threshold: .2
 }).observe(scene);
})();

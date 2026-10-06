document.querySelectorAll('a[href^="#ax-tender-radar"]').forEach(a => a.addEventListener('click', e => {
 e.preventDefault();
 e.stopPropagation();
 const target = document.querySelector(a.getAttribute('href'));
 document.body.classList.remove('noapx');
 target.scrollIntoView({
  behavior: 'instant',
  block: 'start',
  inline: 'start'
 });
}));

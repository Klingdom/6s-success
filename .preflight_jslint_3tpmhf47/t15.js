(function(){
  if(!('IntersectionObserver' in window)){document.querySelectorAll('.reveal').forEach(function(e){e.classList.add('in')});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}})},{threshold:.12});
  document.querySelectorAll('.reveal').forEach(function(e){io.observe(e);});
  setTimeout(function(){var vh=innerHeight;document.querySelectorAll('.reveal:not(.in)').forEach(function(e){if(e.getBoundingClientRect().top<vh*0.95)e.classList.add('in');});},200);
})();
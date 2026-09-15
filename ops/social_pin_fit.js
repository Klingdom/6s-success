<script>
/* Fits a save-and-share card to its canvas, then records what it did on
   <body data-fit data-steps>, which ops/build_social_pins.py reads back from a
   DOM dump. Order: purpose line, picture band, checklist type, one trailing
   item (never below three shown, with a "+ 1 more" line), and only then the
   picture. A card with a picture never hides more than one item: a standard
   such as strapping a cabinet to the wall must not vanish behind a note. */
(function(){
  var H=%(h)d, b=document.body;
  function run(){
    var ul=document.querySelector('ul'), foot=document.querySelector('.foot'),
        art=document.querySelector('.art'), sub=document.querySelector('.sub'),
        steps=[], gap=0.025*H, floor=%(type_floor)s*H;
    function over(){ return ul.getBoundingClientRect().bottom > foot.getBoundingClientRect().top - gap; }
    function shrinkType(){
      var li=ul.querySelector('li'); if (!li) return;
      var fs=parseFloat(getComputedStyle(li).fontSize), start=fs;
      while (over() && fs > floor) {
        fs -= 0.5;
        ul.querySelectorAll('li:not(.more)').forEach(function(x){ x.style.fontSize = fs + 'px'; });
      }
      if (fs < start) steps.push('type ' + fs.toFixed(1) + 'px');
    }
    /* Leave trailing items for the zone page, at most maxDrop of them and never
       fewer than minItems shown. The note sits on one line at the items' size. */
    function dropTrailing(minItems, maxDrop){
      var n=0, more=null;
      while (over() && n < maxDrop) {
        var lis=ul.querySelectorAll('li:not(.more)');
        if (lis.length <= minItems) break;
        var size=getComputedStyle(lis[0]).fontSize;
        lis[lis.length - 1].remove(); n += 1;
        if (!more) { more=document.createElement('li'); more.className='more'; ul.appendChild(more); }
        more.style.fontSize = size;
        more.textContent='+ ' + n + ' more on the zone page';
      }
      if (n) steps.push(n + ' item(s) left for the zone page');
    }
    /* The eyebrow is one line or it is untidy: "PRIMARY BEDROOM · FREE ZONE"
       with "RESET" alone underneath. Shrink it until it fits on one line. */
    var eb=document.querySelector('.eyebrow');
    if (eb) {
      var efs=parseFloat(getComputedStyle(eb).fontSize), estart=efs, lh=function(){ return eb.getBoundingClientRect().height; };
      eb.style.whiteSpace='nowrap';
      while (eb.scrollWidth > eb.clientWidth + 1 && efs > 0.016*H) { efs -= 0.5; eb.style.fontSize = efs + 'px'; }
      if (efs < estart) steps.push('eyebrow ' + efs.toFixed(1) + 'px');
      if (eb.scrollWidth > eb.clientWidth + 1) { eb.style.whiteSpace=''; steps.push('eyebrow wraps'); }
    }
    if (art) {
      if (over() && sub) { sub.remove(); steps.push('purpose dropped'); }
      var ah=art.getBoundingClientRect().height;
      while (over() && ah > %(art_floor)s*H) { ah -= 0.01*H; art.style.height = ah + 'px'; }
      steps.push('picture ' + Math.round(100*ah/H) + '%%');
      shrinkType();
      dropTrailing(3, 1);
      if (over()) {
        art.remove(); steps = ['picture removed: checklist too long to share the canvas'];
        ul.innerHTML = document.getElementById('full-items').innerHTML;
        document.documentElement.classList.remove('has-art');
      }
    }
    if (over()) shrinkType();
    if (over()) dropTrailing(3, 99);
    b.setAttribute('data-steps', steps.join(', '));
    b.setAttribute('data-fit', over() ? 'overflow' : 'ok');
  }
  var faces=['700 40px Inter','600 40px Inter','600 40px Fraunces'];
  Promise.all(faces.map(function(f){ return document.fonts.load(f); })).then(function(r){
    var missing=faces.filter(function(f,i){ return !r[i].length; });
    if (missing.length) { b.setAttribute('data-fit','fonts-missing'); b.setAttribute('data-steps', missing.join(' | ')); return; }
    var img=document.querySelector('.art img');
    if (img && !img.complete) { img.onload=run; img.onerror=function(){ b.setAttribute('data-fit','picture-failed'); }; }
    else run();
  });
})();
</script>

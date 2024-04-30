const textarea = document.getElementById('text');
textarea.addEventListener('keydown', resize);

function resize() {
  var el = this;
  setTimeout(function() {
  if (el.scrollHeight < 100){
    el.style.cssText = 'height:auto; padding:0';
    el.style.cssText = 'height:' + el.scrollHeight + 'px';}
  }, 1);
}
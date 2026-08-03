(function(){
  'use strict';
  var cache = {};
  function esc(text){ var d=document.createElement('div'); d.textContent=text||''; return d.innerHTML; }
  function campoDoFor(valor){ return (valor||'').replace(/^id_/,'').replace(/-\d+-/g,'_'); }
  function textoLabel(label){
    var clone=label.cloneNode(true);
    clone.querySelectorAll('.btn-ajuda-contextual, .required, .asteriskField').forEach(function(el){el.remove();});
    return (clone.textContent||'').replace(/\s+/g,' ').replace(/[:*]+$/,'').trim();
  }
  function criarBotao(label, info){
    if(label.querySelector('.btn-ajuda-contextual')) return;
    var b=document.createElement('button'); b.type='button'; b.className='btn-ajuda-contextual'; b.textContent='?';
    b.dataset.ajudaChave=info.chave; b.title=info.ajuda_curta||'Abrir orientação deste campo'; b.setAttribute('aria-label','Abrir ajuda: '+(info.titulo||'campo'));
    label.appendChild(b);
  }
  function resolverLabels(){
    document.querySelectorAll('label[for]').forEach(function(label){
      var campo=campoDoFor(label.getAttribute('for')); if(!campo) return;
      var rotulo=textoLabel(label);
      var key=location.pathname+'|'+campo+'|'+rotulo;
      if(cache[key]){ if(cache[key].disponivel) criarBotao(label,cache[key]); return; }
      var url='/ajuda-contextual/resolver/?campo='+encodeURIComponent(campo)+'&label='+encodeURIComponent(rotulo)+'&path='+encodeURIComponent(location.pathname);
      fetch(url,{credentials:'same-origin'})
        .then(function(r){return r.json();})
        .then(function(data){cache[key]=data;if(data.disponivel)criarBotao(label,data);})
        .catch(function(){});
    });
  }
  function bloco(titulo,texto,classe){ if(!texto)return ''; return '<section class="ajuda5w2h-bloco '+(classe||'')+'"><h6>'+esc(titulo)+'</h6><p>'+esc(texto)+'</p></section>'; }
  function mostrarModal(){
    if(window.jQuery && window.jQuery.fn && window.jQuery.fn.modal){ window.jQuery('#modalAjudaContextual').modal('show'); return; }
    var el=document.getElementById('modalAjudaContextual');
    if(el){ el.style.display='block'; el.classList.add('show'); el.setAttribute('aria-modal','true'); }
  }
  function abrir(chave){
    var titulo=document.getElementById('tituloAjudaContextual'), conteudo=document.getElementById('conteudoAjudaContextual');
    if(!titulo||!conteudo) return;
    titulo.textContent='Ajuda'; conteudo.innerHTML='<div class="ajuda5w2h-carregando">Carregando orientação...</div>';
    mostrarModal();
    fetch('/ajuda-contextual/'+encodeURIComponent(chave)+'/?path='+encodeURIComponent(location.pathname),{credentials:'same-origin'})
      .then(function(r){if(!r.ok)throw new Error();return r.json();}).then(function(d){
        titulo.textContent=d.titulo||'Ajuda';
        var html='<div class="ajuda5w2h-grid">'+bloco('O que é?',d.what)+bloco('Por que preencher?',d.why)+bloco('Quem é responsável?',d.who)+bloco('Quando preencher?',d.when)+bloco('Onde é utilizado?',d.where)+bloco('Como preencher?',d.how)+bloco('Quanto / impacto',d.how_much)+bloco('Exemplo prático',d.exemplo)+bloco('Atenção',d.atencao,'destaque')+'</div>';
        conteudo.innerHTML=html||'<div class="alert alert-info">A orientação ainda está sendo preparada.</div>';
      }).catch(function(){conteudo.innerHTML='<div class="alert alert-warning">A orientação deste campo ainda não está disponível.</div>';});
  }
  document.addEventListener('click',function(e){var b=e.target.closest('.btn-ajuda-contextual');if(b){e.preventDefault();e.stopPropagation();abrir(b.dataset.ajudaChave);}});
  document.addEventListener('DOMContentLoaded',resolverLabels);
  // Formsets e componentes que surgem depois do carregamento.
  var observer=new MutationObserver(function(){window.clearTimeout(observer._t);observer._t=window.setTimeout(resolverLabels,150);});
  document.addEventListener('DOMContentLoaded',function(){observer.observe(document.body,{childList:true,subtree:true});});
  window.PGPAjudaContextual={atualizar:resolverLabels,abrir:abrir};
})();

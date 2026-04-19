(function(){
  /**
  function addIconToAccount(){
    // Procura por elementos cuja textbox contenha o texto exato 'Account'
    const candidates = Array.from(document.querySelectorAll('*'));
    for (const el of candidates){
      if (el.textContent && el.textContent.toLowerCase().trim().includes('account')){
        if (el.querySelector('.login-icon')) return; // já adicionado
        const icon = document.createElement('i');
        icon.className = 'fas fa-sign-in-alt login-icon';
        icon.style.marginRight = '6px';
        el.insertBefore(icon, el.firstChild);
        return;
      }
    }
  }
  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', addIconToAccount);
  } else {
    addIconToAccount();
  }
  // Observa mudanças no DOM para lidar com carregamento assíncrono
  const observer = new MutationObserver(addIconToAccount);
  observer.observe(document.body, { childList: true, subtree: true });
  **/
})();

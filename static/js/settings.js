// Settings page behavior: accessible tabs, logo preview/remove, confirmations

(function(){
  function showTab(tabName, btnEl) {
    document.querySelectorAll('[id^="tab-"]').forEach(tab => {
      tab.style.display = 'none';
      tab.setAttribute('aria-hidden', 'true');
    });

    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) {
      targetTab.style.display = 'block';
      targetTab.setAttribute('aria-hidden', 'false');
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
      btn.setAttribute('aria-selected', 'false');
    });

    if (btnEl) {
      btnEl.classList.add('active');
      btnEl.setAttribute('aria-selected', 'true');
      btnEl.focus();
    } else {
      const btn = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
      if (btn) {
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
      }
    }
  }

  function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
      btn.addEventListener('click', function(e){
        const tab = this.dataset.tab;
        showTab(tab, this);
      });

      // keyboard navigation
      btn.addEventListener('keydown', function(e){
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          const tabs = Array.from(tabButtons);
          const idx = tabs.indexOf(this);
          const next = e.key === 'ArrowRight' ? tabs[(idx+1)%tabs.length] : tabs[(idx-1+tabs.length)%tabs.length];
          next.focus();
          next.click();
          e.preventDefault();
        }
      });
    });

    // Load tab from URL param
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab) {
      showTab(tab);
    }
  }

  function initLogoPreview() {
    const logoInput = document.getElementById('logoInput');
    if (!logoInput) return;

    logoInput.addEventListener('change', function(e){
      if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = function(ev) {
          const previewContainer = document.querySelector('.logo-preview-container') || document.createElement('div');
          previewContainer.className = 'logo-preview-container';
          previewContainer.innerHTML = `\n            <img src="${ev.target.result}" class="logo-preview" alt="Nouveau logo">\n            <button type="button" class="logo-remove"><i class="fas fa-times"></i></button>\n          `;

          const uploadArea = document.querySelector('.logo-upload-area');
          if (uploadArea) uploadArea.insertAdjacentElement('afterend', previewContainer);

          const removeBtn = previewContainer.querySelector('.logo-remove');
          if (removeBtn) removeBtn.addEventListener('click', removeLogo);
        };
        reader.readAsDataURL(this.files[0]);
      }
    });
  }

  function removeLogo() {
    const container = document.querySelector('.logo-preview-container');
    if (container) container.remove();
    const logoInput = document.getElementById('logoInput');
    if (logoInput) logoInput.value = '';
  }

  function initConfirmations() {
    document.addEventListener('click', function(e){
      const el = e.target.closest('.btn-danger-custom');
      if (!el) return;
      if (!confirm('Êtes-vous sûr de vouloir effectuer cette action ?')) {
        e.preventDefault();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    initTabs();
    initLogoPreview();
    initConfirmations();
  });
})();

function switchLabTab(btn, showId, hideId1, hideId2) {
    const showEl = document.getElementById(showId);
    const hideEl1 = document.getElementById(hideId1);
    const hideEl2 = document.getElementById(hideId2);

    if (showEl) showEl.classList.remove('hidden');
    if (hideEl1) hideEl1.classList.add('hidden');
    if (hideEl2) hideEl2.classList.add('hidden');

    const parent = btn.parentElement;
    parent.querySelectorAll('.tab-btn').forEach(b => {
        b.className = 'tab-btn px-3 py-1 rounded-md bg-transparent text-zinc-400 hover:text-white border border-transparent transition-colors font-mono text-xs';
    });
    btn.className = 'tab-btn px-3 py-1 rounded-md bg-zinc-800 text-white border border-zinc-600 transition-colors font-semibold font-mono text-xs';
}

function setLanguage(lang) {
    if (lang === 'th') {
        document.documentElement.classList.add('th-mode');
        if (document.body) document.body.classList.add('th-mode');
        document.cookie = "lab_lang=th; path=/; max-age=31536000; SameSite=Lax";
        updateLangButtonState('th');
    } else {
        document.documentElement.classList.remove('th-mode');
        if (document.body) document.body.classList.remove('th-mode');
        document.cookie = "lab_lang=en; path=/; max-age=31536000; SameSite=Lax";
        updateLangButtonState('en');
    }
}

function updateLangButtonState(lang) {
    const btnEn = document.getElementById('btn-lang-en');
    const btnTh = document.getElementById('btn-lang-th');
    if (btnEn && btnTh) {
        if (lang === 'th') {
            btnTh.className = 'px-2 py-0.5 rounded-md text-[10px] font-mono font-bold bg-white text-black border border-white transition-colors';
            btnEn.className = 'px-2 py-0.5 rounded-md text-[10px] font-mono text-zinc-400 hover:text-white border border-transparent transition-colors';
        } else {
            btnEn.className = 'px-2 py-0.5 rounded-md text-[10px] font-mono font-bold bg-white text-black border border-white transition-colors';
            btnTh.className = 'px-2 py-0.5 rounded-md text-[10px] font-mono text-zinc-400 hover:text-white border border-transparent transition-colors';
        }
    }
}

function initLanguage() {
    const match = document.cookie.match(/(?:^|;\s*)lab_lang=([^;]*)/);
    const lang = match ? match[1] : 'en';
    if (lang === 'th') {
        document.documentElement.classList.add('th-mode');
        if (document.body) document.body.classList.add('th-mode');
        updateLangButtonState('th');
    } else {
        updateLangButtonState('en');
    }
}

document.addEventListener('DOMContentLoaded', initLanguage);

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

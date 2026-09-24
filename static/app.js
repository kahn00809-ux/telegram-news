const refreshButton = document.querySelector('#refreshButton');

refreshButton.addEventListener('click', async () => {
    refreshButton.disabled = true;
    refreshButton.querySelector('span').textContent = '…';
    try {
        const response = await fetch('/api/refresh', { method: 'POST' });
        if (!response.ok) throw new Error('refresh failed');
        window.location.reload();
    } catch (error) {
        refreshButton.disabled = false;
        refreshButton.querySelector('span').textContent = '↻';
        refreshButton.lastChild.textContent = ' Ошибка обновления';
    }
});

/* ============================================================
   main.js — SPK Indosat Ooredoo Hutchison
   Global JavaScript utilities
   ============================================================ */

/**
 * Tampilkan toast notification
 * @param {string} msg   - Pesan yang ditampilkan
 * @param {string} type  - 'success' | 'error' | 'info' | 'warn'
 */
function showToast(msg, type = 'success') {
    const colors = {
        success: { bg: '#E5F7EE', color: '#006B35', border: '#00A651', icon: 'check-circle-fill' },
        error:   { bg: '#FFF0F3', color: '#E4002B', border: '#E4002B', icon: 'x-circle-fill' },
        info:    { bg: '#E5F7FD', color: '#0077A3', border: '#00B5E2', icon: 'info-circle-fill' },
        warn:    { bg: '#FFFBEA', color: '#8B6200', border: '#FFD100', icon: 'exclamation-triangle-fill' },
    };
    const c = colors[type] || colors.success;

    const t = document.createElement('div');
    t.style.cssText = `
        position: fixed; bottom: 24px; right: 24px; z-index: 9999;
        padding: 12px 20px; border-radius: 10px; font-size: 13.5px; font-weight: 600;
        box-shadow: 0 4px 20px rgba(0,0,0,.15); animation: fadeIn .3s ease;
        background: ${c.bg}; color: ${c.color};
        border-left: 4px solid ${c.border};
        display: flex; align-items: center; gap: 10px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    `;
    t.innerHTML = `<i class="bi bi-${c.icon}"></i>${msg}`;
    document.body.appendChild(t);
    setTimeout(() => {
        t.style.opacity = '0';
        t.style.transition = 'opacity .3s';
        setTimeout(() => t.remove(), 300);
    }, 3000);
}

/**
 * Format angka ke format Rupiah singkat
 * @param {number} val
 */
function formatMRC(val) {
    return 'Rp ' + parseFloat(val).toLocaleString('id-ID') + ' jt';
}

/**
 * Konfirmasi hapus dengan dialog sederhana
 * @param {string} msg
 */
function konfirmHapus(msg = 'Yakin ingin menghapus data ini?') {
    return confirm(msg);
}


document.addEventListener('DOMContentLoaded', function () {
    const copyBtn = document.getElementById('error-copy-btn');
    const errorIdText = document.getElementById('errorId');
    if (copyBtn) {
        copyBtn.addEventListener('click', getBtnCopyListener(copyBtn, errorIdText));
    }
});
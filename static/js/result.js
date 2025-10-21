document.addEventListener('DOMContentLoaded', function () {
    const copyButton = document.getElementById('copy-output-btn');
    const outputText = copyButton.nextElementSibling;

    if (copyButton && outputText) {
        copyButton.addEventListener('click', getBtnCopyListener(copyButton, outputText));
    }
});

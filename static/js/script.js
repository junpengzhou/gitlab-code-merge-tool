function getBtnCopyListener(copyButton, outputText) {
    return function () {
        const originalText = copyButton.textContent;
        const textToCopy = outputText.textContent;

        // 检查是否支持 Clipboard API
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textToCopy).then(function () {
                copyButton.textContent = '🥳复制成功';
                setTimeout(() => {
                    copyButton.textContent = originalText;
                }, 2000);
            }).catch(function (err) {
                console.error('复制失败: ', err);
                fallbackCopyTextToClipboard(textToCopy, copyButton, originalText);
            });
        } else {
            // 降级到传统方法
            fallbackCopyTextToClipboard(textToCopy, copyButton, originalText);
        }
    };
}

function fallbackCopyTextToClipboard(text, button, originalText) {
    const textArea = document.createElement("textarea");
    textArea.value = text;

    // 避免滚动到底部
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    textArea.style.opacity = "0";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        const successful = document.execCommand('copy');
        if (successful) {
            button.textContent = '🥳复制成功';
            setTimeout(() => {
                button.textContent = originalText;
            }, 2000);
        } else {
            alert('复制失败，请手动复制');
        }
    } catch (err) {
        console.error('复制失败: ', err);
        alert('复制失败，请手动复制' + originalText);
    }

    document.body.removeChild(textArea);
}
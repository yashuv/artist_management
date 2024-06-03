if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

setTimeout(function () {
    var errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}, 3000);
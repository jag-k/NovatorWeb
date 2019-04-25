function loadFile(event, input) {
    let output = document.getElementById(input.getAttribute('for'));
    output.src = URL.createObjectURL(event.target.files[0]);
    console.log(output.src);
    console.log(output)
}

function loadingButton(btn) {
    console.log("Loading:", btn);
    btn.innerHTML =
        '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' +
        'Загрузка...'
}

document.querySelectorAll('button .btn [type=submit]').forEach(function (elem) {
    console.log(elem);
    elem.setAttribute('onclick', "loadingButton(this)")
});
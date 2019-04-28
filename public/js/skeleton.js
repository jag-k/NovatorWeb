function loadFile(event, input) {
    let output = document.getElementById(input.getAttribute('for'));
    document.querySelectorAll('.custom-file-label[for="' + input.id + '"]').forEach(function (value) {
        value.innerHTML = event.target.files[0].name
    });

    output.classList.add('img-thumbnail');
    output.classList.add('mb-3');
    output.src = URL.createObjectURL(event.target.files[0]);
}

function loadingButton(btn) {
    if (btn.parentElement.checkValidity()) {
        btn.innerHTML =
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ' +
            'Загрузка...'
    }
}

document.querySelectorAll('button.btn[type=submit]').forEach(function (elem) {
    elem.setAttribute('onclick', "loadingButton(this)")
});

document.querySelectorAll("label").forEach(function (elem) {
    let for_id = elem.getAttribute('for');
    if (for_id && document.getElementById(for_id).required) {
        elem.innerHTML += ' <span class="text-danger">*</span>'
    }
});

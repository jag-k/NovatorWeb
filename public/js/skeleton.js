function loadImage(event, input) {
    let output = document.getElementById(input.getAttribute('for'));
    loadFile(event, input);

    output.classList.add('img-thumbnail');
    output.classList.add('mb-3');
    output.classList.remove('hide');
    output.src = URL.createObjectURL(event.target.files[0]);
}

function loadFile(event, input) {
    console.log(event);
    console.log(input);
    document.querySelectorAll('.custom-file-label[for="' + input.id + '"]').forEach(function (value) {
        console.log(value);
        value.innerHTML = event.target.files[0].name
    });
}

function loadingButton(btn) {
    if (btn.parentElement.checkValidity()) {
        btn.innerHTML =
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ' +
            'Загрузка...'
    }
}
let del_data = {};
function del_selector(elem) {
    let f = elem.getAttribute('for');
    let form = document.getElementById(f);
    if (elem.checked) {
        del_data[f] = form.innerHTML;
        form.innerHTML = '';
        elem.name = elem.getAttribute('_name');
    } else {
        form.innerHTML = del_data[f];
        elem.name = '';
    }
}

document.querySelectorAll('button.btn[type=submit]').forEach(function (elem) {
    elem.setAttribute('onclick', "loadingButton(this)")
});

document.querySelectorAll("label:not(.custom-file-label)").forEach(function (elem) {
    let for_id = elem.getAttribute('for');
    if (for_id && document.getElementById(for_id).required) {
        elem.innerHTML += ' <span class="text-danger">*</span>'
    }
});

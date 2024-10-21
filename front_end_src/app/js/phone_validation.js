'use strict';
// Phone validation
    // '/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im'
const submit_btn = document.querySelector('button[type="submit"]');
const phone_input = document.querySelector('.phone_input');

const checkbox1 = document.getElementById('oferta');
const checkbox2 = document.getElementById('pd');

const checkbox_required = checkbox1 && checkbox2;

const check_phone = (str) => {
    return (/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im).test(str);
}

const toggle_sumbit = (str) => {
    if (check_phone(str)) {
        if (checkbox_required && !check_checkboxes()) return;
        submit_btn.disabled = false;
        if (!submit_btn.classList.contains('sumbit_active')) submit_btn.classList.toggle('sumbit_active');
    }
    else {
        if (submit_btn.classList.contains('sumbit_active')) submit_btn.classList.toggle('sumbit_active');
        submit_btn.disabled = true;
    }
}

phone_input.addEventListener('input', (e) => {
    console.log('entered');
    let target = e.target;
    toggle_sumbit(target.value);
})



const check_checkboxes = () => {
    if (checkbox1.checked && checkbox2.checked && check_phone(phone_input.value)) {
        submit_btn.disabled = false;
        if (!submit_btn.classList.contains('sumbit_active')) submit_btn.classList.toggle('sumbit_active');
    } else {
        submit_btn.disabled = true;
        if (submit_btn.classList.contains('sumbit_active')) submit_btn.classList.toggle('sumbit_active');
    }
}

if (checkbox1 && checkbox2) {
    checkbox1.addEventListener('change', check_checkboxes);
    checkbox2.addEventListener('change', check_checkboxes);
}
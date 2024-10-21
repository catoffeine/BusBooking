window.onload = () => {
    const PASSWORD_REQUIRED_LENGTH = 8;

    const capital_req = document.querySelector('.setpassword_container .capital');
    const lowercase_req = document.querySelector('.setpassword_container .lowercase');
    const number_req = document.querySelector('.setpassword_container .number');
    const length_req = document.querySelector('.setpassword_container .length');

    const password_input = document.querySelector('form .password_input');
    const password_sumbitbtn = document.querySelector('form button');
    password_sumbitbtn.disabled = true;

    const checkbox1 = document.getElementById('oferta');
    const checkbox2 = document.getElementById('pd');
    const checkbox_exist = checkbox1 && checkbox2;
    const submitButton = document.getElementById('submitBtn');

    const check_checkboxes = () => {
        return checkbox1.checked && checkbox2.checked;
    }

    const toggle_active = () => {
        if (check_password_requirements()) {
            if (checkbox_exist) {
                if (check_checkboxes()) {
                    if (!password_sumbitbtn.classList.contains('form_button_active')) {
                        password_sumbitbtn.classList.toggle('form_button_active');
                        password_sumbitbtn.disabled = false;
                    }
                } else {
                    if (password_sumbitbtn.classList.contains('form_button_active')) {
                         password_sumbitbtn.classList.toggle('form_button_active');
                         password_sumbitbtn.disabled = true;
                    }
                }
            } else {
                if (!password_sumbitbtn.classList.contains('form_button_active')) {
                    password_sumbitbtn.classList.toggle('form_button_active');
                    password_sumbitbtn.disabled = false;
                }
            }
        } else {
            if (password_sumbitbtn.classList.contains('form_button_active')) {
                password_sumbitbtn.classList.toggle('form_button_active');
                password_sumbitbtn.disabled = true;
            }
        }
    }
  
    if (checkbox_exist) {
        checkbox1.addEventListener('change', toggle_active);
        checkbox2.addEventListener('change', toggle_active);
    }
    

    const check_password_requirements = () => {
        console.log('entered');
        const password = password_input.value;
        const capital_req_state = capital_req.classList.contains('satisfied');
        const lowercase_req_state = lowercase_req.classList.contains('satisfied');
        const number_req_state = number_req.classList.contains('satisfied');
        const length_req_state = length_req.classList.contains('satisfied');

        const regex_capital = (new RegExp(/^(.*[A-Z].*)$/)).test(password);
        const regex_lowercase = (new RegExp(/^(.*[a-z].*)$/)).test(password);
        const regex_number = (new RegExp(/^(.*[0-9].*)$/)).test(password);
        const length_check = password.length >= PASSWORD_REQUIRED_LENGTH;

        const is_sumbit_btn_disabled = password_sumbitbtn.disabled;

        if ((regex_capital && !capital_req_state) || (!regex_capital && capital_req_state)) {
            capital_req.classList.toggle('satisfied');
        }

        if ((regex_lowercase && !lowercase_req_state) || (!regex_lowercase && lowercase_req_state)) {
            lowercase_req.classList.toggle('satisfied');
        }

        if ((regex_number && !number_req_state) || (!regex_number && number_req_state)) {
            number_req.classList.toggle('satisfied');
        }

        if ((length_check && !length_req_state) || (!length_check && length_req_state)) {
            length_req.classList.toggle('satisfied');
        }

        if (regex_capital && regex_lowercase && regex_number && length_check) {
            return true;
        }
        // else if (!regex_capital || !regex_lowercase || !regex_number || !length_check) {
        //     return false;
        // }
        return false;
    }

    password_input.addEventListener('input', toggle_active);
}
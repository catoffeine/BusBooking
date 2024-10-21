let code_input_container = document.querySelector('.personcode_form .flexcontainer .code_input');
let code_input_items = code_input_container.querySelectorAll('.item input');
let code_input_register_btn = document.querySelector('.personcode_form .flexcontainer button');
let hidden_code_input = document.querySelector('.personcode_form .hidden_input input');

const check_code_input = (target) => {
    let flag = false;
    let value_code = '';
    for (let i = 0; i < code_input_items.length; ++i) {
        value_code += code_input_items[i].value;
        if (code_input_items[i].value == '' && code_input_items[i] !== target) {
            code_input_items[i].focus();
            flag = true;
            break;
        }
    }
    if (!flag) {
        hidden_code_input.value = value_code;
        console.log(hidden_code_input.value);
        code_input_register_btn.focus();
    }
}

code_input_items.forEach((element) => {
    element.addEventListener('input', (e) => {
        console.log('onchange');
        let target = e.target;
        console.log(isNaN(target.value))
        if (isNaN(target.value)) target.value = '';
        else if (target.value.length > 1) target.value = target.value.substring(0, target.value.length - 1);
        
        else {
            setTimeout(() => {
                check_code_input(target);  
            }, 0);
        }

    })
})

// const generate_code_input = () => {
//     const code_input = document.createElement('div');
//     code_input.classList.add('code_input');

//     for (let i = 0; i < CODE_LENGTH; ++i) {
//         const item = document.createElement('div');
//         item.classList.add('item');
//         const input = document.createElement('input');
//         input.type = "number";
//         item.appendChild(input);
//         code_input.appendChild(item);
//     }    
// }

let currentFocus = -1;

document.querySelector('body').onclick = (e) => {
    if (e.target.tagName.toLowerCase() == 'input') return;
    document.querySelectorAll('datalist').forEach(element => {
        element.style.display = 'none';
    })
    
}

document.querySelectorAll('.datalist-control').forEach((element, i) => {

    let input = element.querySelector('input[type="text"]');
    let datalist = element.querySelector('datalist');
    // input.onfocus = () => {
    //     datalist.style.display = 'block';
    // }

    input.onclick = () => {
        document.querySelectorAll('.datalist-control').forEach(element => {
            let datalist_inner = element.querySelector('datalist');
            let input_inner = element.querySelector('input[type="text"]');

            if (datalist_inner.style.display == 'block' && input_inner != input) datalist_inner.style.display = 'none';
        });

        if (datalist.style.display == 'block') datalist.style.display = 'none';
        else datalist.style.display = 'block';
    }

    for (let option of datalist.options) {
        option.onclick = () => {
            input.value = option.value;
            datalist.style.display = 'none';
        }
    };

    input.oninput = (e) => {
        let target = e.target;
        currentFocus = -1;
        let text = target.value.toUpperCase();
        for (let option of datalist.options) {
            if(option.value.toUpperCase().indexOf(text) > -1){
                option.style.display = "block";
            } else {
                option.style.display = "none";
            }
        };
    };

    input.onkeydown = (e) => {
        if(e.keyCode == 40){
            currentFocus++
            addActive(datalist.options);
        }
        else if(e.keyCode == 38){
            currentFocus--
            addActive(datalist.options);
        }
        else if(e.keyCode == 13){
            e.preventDefault();
            if (currentFocus > -1) {
                 /*and simulate a click on the "active" item:*/
                if (datalist.options) datalist.options[currentFocus].click();
            }
        }
    }

});


function addActive(x) {
    if (!x) return false;
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    x[currentFocus].classList.add("active");
}

function removeActive(x) {
    for (let i = 0; i < x.length; i++) {
        x[i].classList.remove("active");
    }
}

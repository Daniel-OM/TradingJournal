

// Format currency values
function formatCurrency (value, min_decimals = 1, max_decimals = 2, notation = null) {
    // Use notation = 'compact' for financial amounts
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: min_decimals,
        maximumFractionDigits: max_decimals,
        notation: notation
    }).format(value);
}

// Format percentage values
function formatPercentage (value, min_decimals = 1, max_decimals = 2) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: min_decimals,
        maximumFractionDigits: max_decimals
    }).format(value / 100);
}

// Format compact values
function formatFinancial (value, min_decimals = 1, max_decimals = 2, notation = null) {
    // Use notation = 'compact' for financial amounts
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: min_decimals,
        maximumFractionDigits: max_decimals,
        notation: notation
    }).format(value);
}

function formatNumber (n, mode = null, min_decimals = 1, max_decimals = 2, notation = null) {
    // Use notation = 'compact' for financial amounts
    if (mode === 'currency') {
        return formatCurrency(n, min_decimals, max_decimals, notation);
    } else if (mode === 'percentage') {
        return formatPercentage(n, min_decimals, max_decimals);
    } else if (mode == 'financial') {
        return formatFinancial(n, min_decimals, max_decimals, notation);
    } else {
        return n.toFixed(max_decimals);
    }
}

function zeroPad (num, length) {
    length = length || 2; // defaults to 2 if no parameter is passed
    return (new Array(length).join('0')+num.toString()).slice(length*-1);
};


function formatDate (dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}








function triggerChange (element) {
    element.dispatchEvent(new Event('change', { bubbles: true }));
}

function triggerInput (element) {
    element.dispatchEvent(new Event('input', { bubbles: true }));
}

// Check if passwords match
function checkPasswords (name, repeat_name) {
    var input = document.querySelector(`[name="${name}"]`);
    if (input.value != document.querySelector(`[name="${repeat_name}"]`).value) {
        input.setCustomValidity('Password Must be Matching.');
        return false;
    } else {
        // input is valid -- reset the error message
        input.setCustomValidity('');
        return true;
    }
}


async function post (url, data = null, callback = () => { }, files = [], raise = true) {

    $.ajax({
        type: 'POST',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('User', true);
        },
        xhrFields: {
            withCredentials: true // Incluye cookies en la solicitud
        },
        url: url,
        contentType: 'application/json',
        data: data, //JSON.stringify(data),
        files: files,
        dataType: 'json',
        success: function (response) {
            if (raise) {
                if (response.executed) {
                    if (callback != null)
                        callback(response);
                } else {
                    alert(`${response.description} ${response.data}`);
                }
            } else {
                if (callback != null)
                    callback(response);
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            if (![0, '0'].includes(xhr.status) && ![undefined].includes(thrownError)) {
                alert(xhr.responseText, thrownError, 'error');
            }
        }
    });
}
async function get (url, callback = () => { }, params = null, error = null, raise = true) {

    if (params != null & false) {
        url += '?';
        let c = 0;
        for (const [key, value] of Object.entries(params)) {
            if (c > 0)
                url += '&';
            url += `${key}=${value}`;
        }
    }
    $.ajax({
        type: 'GET',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('User', true);
        },
        xhrFields: {
            withCredentials: true // Incluye cookies en la solicitud
        },
        url: url,
        data: params,
        success: function (response) {
            console.log(url, response);
            if (raise) {
                if (response.executed) {
                    if (callback != null)
                        callback(response);
                } else {
                    alert(`${response.description} ${response.data}`);
                }
            } else {
                if (callback != null)
                    callback(response);
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            //console.log(ajaxOptions);
            if (![0, '0'].includes(xhr.status) && ![undefined].includes(thrownError)) {
                if (typeof error === "function") {
                    error();
                } else {
                    alert(xhr.status + thrownError + 'error');
                }
            }
        }
    });
}

async function getReturn (url, params = null) {

    if (params != null) {
        url += '?';
        let c = 0;
        for (const [key, value] of Object.entries(params)) {
            if (c > 0)
                url += '&';
            url += `${key}=${value}`;
        }
    }

    return await (await fetch(url, {
        method: 'GET',
        credentials: 'include', // Incluye cookies en la solicitud
    })).json();
}

async function submitForm (id, url, change_select = true, submit = false, func = () => { }) {

    let form = document.getElementById(id);
    if (checkPasswords('password', 'pass_confirm')) {

        if (change_select) {
            form.getElementsByTagName('select').forEach(function (select) {
                let input = document.createElement('input');
                input.name = select.id;
                input.value = select.value;
                form.appendChild(input);
            });
            // Select2
            form.querySelectorAll('select.select2').forEach(function (select) {
                let input = document.createElement('input');
                input.name = select.id;
                input.value = select.value;
                form.appendChild(input);
            });
        }

        if (submit) {
            form.action = url;
            form.method = 'post';
            form.submit();
            form.action = '';
        } else {
            let formData = new FormData(form);
            var object = {};
            formData.forEach(function (value, key) {
                object[key] = value;
            });
            console.log(object);
            await post(url, object, func);
        }
    }
}

function setCookie (name, value) {
    document.cookie = `${name}=${value}`;
}

function getCookie (name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2)
        return parts.pop().split(';').shift();
    else
        return null;
}

function setLocalStorage (name, value) {
    localStorage.setItem(name, value);
}

function getLocalStorage (name) {
    return localStorage.getItem(name);
}

function capitalize (string) {
    const words = string.split(" ");

    for (let i = 0; i < words.length; i++) {
        words[i] = words[i][0].toUpperCase() + words[i].substr(1);
    }

    return words.join(" ");
}

async function originalPost (url, data = null, callback = () => { }) {
    console.log(data);
    const requestOptions = {
        headers: {
            'Content-Type': 'application/json',
            'User': true,
        },
        credentials: 'include', // Incluye cookies en la solicitud
        // mode: "no-cors",
        method: 'POST',
        contentType: 'multipart/form-data',
        body: data,
        dataType: 'json',
    };

    await fetch(url, requestOptions).then(
        onfulfilled = async function (response) {
            console.log(response.data);
            callback();
        },
        onrejected = async function () {
            console.log('Error');
        }
    );
}

async function postFiles (url, data = null, callback = () => { }, files = []) {

    var form_data = new FormData();
    for (var key in data) {
        form_data.append(key, data[key]);
    }
    form_data.forEach((key, value) => { console.log(key, value); });

    for (let file of files) {
        form_data.append('files', file);
    }

    $.ajax({
        type: 'POST',
        async: true,
        beforeSend: function (xhr) {
            xhr.setRequestHeader('User', true);
        },
        xhrFields: {
            withCredentials: true // Incluye cookies en la solicitud
        },
        url: url,
        contentType: false,// 'multipart/form-data',
        data: form_data,
        processData: false,
        // dataType: 'json',
        success: function (response) {
            if (response.executed) {
                if (callback != null)
                    callback(response.data);
            } else {
                alert(response.description);
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(xhr.status, thrownError, 'error');
        }
    });
};


function contains (selector, text) {
    var elements = document.querySelectorAll(selector);
    return Array.prototype.filter.call(elements, function (element) {
        return RegExp(text).test(element.textContent);
    });
}

function validatePassword (password) {
    // Expresiones regulares para cada condición
    const uppercase = /[A-Z]/;
    const lowercase = /[a-z]/;
    const characters = /[0-9!@#$%^&*(),.?":{}|<>]/;
    const min_length = 8;

    if (password.length >= min_length &&
        uppercase.test(password) &&
        lowercase.test(password) &&
        characters.test(password)) {
        return true;
    } else {
        return false;
    }
}

function toggleModal (modal) {
    modal.classList.add('show');
    modal.dataset.ariahidden = true;
    modal.tabindex = -1;
    modal.style.display = 'block';
}

function hideModal (modal) {
    modal.classList.remove('show');
    modal.dataset.ariahidden = false;
    modal.tabindex = -1;
    modal.style.display = 'none';
}


function floatRound (number, decimals = 2) {
    // return Number(Math.floor(value + 'e' + decimals) + 'e-' + decimals);
    return (Math.floor(number * 10 ** decimals) / 10 ** decimals).toFixed(decimals);
}

function getQueryString () {
    return new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
    });
}

function getUrlLast (i = -1) {
    const url = window.location.href.split('/');
    return url[url.length + i];
}



function initializeSelect () {
    var e = $(".selectpicker"),
        t = $(".select2"),
        n = $(".select2-icons");
    function i (e) {
        return e.id
            ? "<i class='" + $(e.element).data("icon") + " me-2'></i>" + e.text
            : e.text;
    }
    e.length && e.selectpicker(),
        t.length && t.each(function () {
            var e = $(this);
            e.wrap('<div class="position-relative"></div>').select2({
                placeholder: "Select value",
                dropdownParent: e.parent(),
            });
        }),
        n.length && n.wrap('<div class="position-relative"></div>').select2({
            dropdownParent: n.parent(),
            templateResult: i,
            templateSelection: i,
            escapeMarkup: function (e) {
                return e;
            },
        });
};

function applySelect (element) {
    var e = $(element);
    e.wrap('<div class="position-relative"></div>').select2({
        placeholder: "Select value",
        dropdownParent: e.parent(),
    });
}

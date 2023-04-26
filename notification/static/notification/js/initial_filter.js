function set_selected_filter(filter_form, key_name) {
    const query_params = new URLSearchParams(window.location.search);
    const selected_key = query_params.get(key_name);

    if (selected_key) {
        filter_form.elements[key_name].value = selected_key;
    }
}

function update_filter(filter_form, key_name) {
    const selected_key = filter_form.elements[key_name].value;

    // 构建新的 URL
    const query_params = new URLSearchParams(window.location.search);

    const query_key = query_params.get(key_name)

    if (query_key !== selected_key) {
        query_params.set(key_name, selected_key)
    }

    // 跳转到新的 URL
    window.location.href = `${window.location.pathname}?${query_params.toString()}`;
}


function initial_filter(form_id, key_name) {
    document.addEventListener('DOMContentLoaded', () => {
        const filter_form = document.getElementById(form_id);

        set_selected_filter(filter_form, key_name);

        const inputs = filter_form.elements[key_name];

        for (const input of inputs) {
            input.addEventListener("change", () => {
                update_filter(filter_form, key_name);
            });
        }
    });
}




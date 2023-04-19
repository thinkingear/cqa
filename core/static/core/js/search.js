

// 获取筛选表单和表单元素
const searchFilterForm = document.getElementById('search-filter-form');
const searchContentTypeInputs = searchFilterForm.elements['search-content-type'];
const searchTimeInputs = searchFilterForm.elements['search-time'];

function setSeartchSelectedFilters() {
    const queryParams = new URLSearchParams(window.location.search);
    const selectedContentType = queryParams.get('type');
    const selectedTime = queryParams.get('time');

    if (selectedContentType) {
        searchFilterForm.elements['search-content-type'].value = selectedContentType;
    }
    if (selectedTime) {
        searchFilterForm.elements['search-time'].value = selectedTime;
    }
}

document.addEventListener('DOMContentLoaded', setSeartchSelectedFilters);


// 添加事件监听器
for (const input of searchContentTypeInputs) {
    input.addEventListener('change', updateSearchFilters);
}
for (const input of searchTimeInputs) {
    input.addEventListener('change', updateSearchFilters);
}

// 更新筛选条件
function updateSearchFilters() {
    const selectedContentType = searchContentTypeInputs.value;
    const selectedTime = searchTimeInputs.value;

    // 构建新的 URL
    const queryParams = new URLSearchParams(window.location.search);

    const queryType = queryParams.get('type')
    const queryTime = queryParams.get('time')

    if (queryType !== selectedContentType) {
        queryParams.set('type', selectedContentType)
    }

    if (queryTime !== selectedTime) {
        queryParams.set('time', selectedTime)
    }

    // 跳转到新的 URL
    window.location.href = `${window.location.pathname}?${queryParams.toString()}`;
}

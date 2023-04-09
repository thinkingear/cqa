function setSelectedFilters() {
    const queryParams = new URLSearchParams(window.location.search);
    const selectedContentType = queryParams.get('type');
    const selectedTime = queryParams.get('time');

    if (selectedContentType) {
        filterForm.elements['content-type'].value = selectedContentType;
    }
    if (selectedTime) {
        filterForm.elements['time'].value = selectedTime;
    }
}

document.addEventListener('DOMContentLoaded', setSelectedFilters);


// 获取筛选表单和表单元素
const filterForm = document.getElementById('filter-form');
const contentTypeInputs = filterForm.elements['content-type'];
const timeInputs = filterForm.elements['time'];

// 添加事件监听器
for (const input of contentTypeInputs) {
    input.addEventListener('change', updateFilters);
}
for (const input of timeInputs) {
    input.addEventListener('change', updateFilters);
}

// 更新筛选条件
function updateFilters() {
    const selectedContentType = filterForm.elements['content-type'].value;
    const selectedTime = filterForm.elements['time'].value;

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

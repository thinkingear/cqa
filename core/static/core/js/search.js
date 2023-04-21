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


function setSortedBy() {
    const queryParams = new URLSearchParams(window.location.search);

    if (queryParams.get('type') === 'course' && queryParams.get('sort') !== 'latest') {
        queryParams.set('sort', 'latest');
        window.location.href = `${window.location.pathname}?${queryParams.toString()}`;
        return;
    }

    const sortedByForm = document.querySelector("#sorted-by-form");

    sortedByForm.elements['sort-by'].value = queryParams.get('sort');
}

document.addEventListener('DOMContentLoaded', setSortedBy);

function updateSortedBy(element) {
    const sortedByForm = document.querySelector("#sorted-by-form");

    const sortedBy = sortedByForm.elements['sort-by'].value;

    const queryParams = new URLSearchParams(window.location.search);

    const querySortedBy = queryParams.get('sort');

    if (querySortedBy !== sortedBy) {
        queryParams.set('sort', sortedBy);
    }

    window.location.href = `${window.location.pathname}?${queryParams.toString()}`;
}

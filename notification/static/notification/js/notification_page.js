function setNotificationSelectedFilter() {
    const notificationFilterForm = document.getElementById('notification-filter-form');
    const queryParams = new URLSearchParams(window.location.search);
    const selectedType = queryParams.get("type");


    if (selectedType) {
        notificationFilterForm.elements["type"].value = selectedType;
    }
}

function updateNotificationFilter() {
    const notificationFilterForm = document.getElementById('notification-filter-form');
    const selectedType = notificationFilterForm.elements["type"].value;

    // 构建新的 URL
    const queryParams = new URLSearchParams(window.location.search);

    const queryType = queryParams.get('type')

    if (queryType !== selectedType) {
        queryParams.set('type', selectedType)
    }

    // 跳转到新的 URL
    window.location.href = `${window.location.pathname}?${queryParams.toString()}`;

}

document.addEventListener('DOMContentLoaded', () => {
    setNotificationSelectedFilter();

    const notificationFilterForm = document.getElementById('notification-filter-form');
    const notificationInputs = notificationFilterForm.elements["type"];

    for (const input of notificationInputs) {
        input.addEventListener("change", updateNotificationFilter);
    }
});

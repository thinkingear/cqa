function toggleTagsConfirmButton(element) {
    // 获取表单元素
    const form = element.closest('.tags-form');
    const content_type = form.dataset.contentType;
    const content_id = form.dataset.contentId;
    const tagsSelect = form.querySelector('.form-select');

    // 获取选中的标签
    const selectedTags = Array.from(tagsSelect.selectedOptions).map(option => option.value);

    // 创建请求数据
    const formData = new FormData();
    // formData.append('content_type', content_type);
    formData.append('content_id', content_id);
    selectedTags.forEach((tag) => {
        formData.append('tags[]', tag);
    })

    let app_name = ''
    if (content_type === 'question') {
        app_name = 'qa';
    } else if (content_type === 'article') {
        app_name = 'pubedit';
    }

    service.post(`/${app_name}/${content_type}/tag/`, formData)
    .then((response) => {

    }).catch((error) => {
        console.log(error);
    })

}






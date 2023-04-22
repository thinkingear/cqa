function toggleReadMoreButton(element, content_type, content_id, user_id) {
    const row = element.parentElement;
    const contentContent = row.previousElementSibling.querySelector('.content-content');
    const readMore = row.querySelector('.read-more');
    const collapseContent = row.querySelector('.collapse-content');

    contentContent.style.maxHeight = 'none';
    readMore.style.display = 'none';
    collapseContent.style.display = '';

    service.get('/history/', {
        params: {
            content_type: content_type,
            content_id: content_id,
            user_id: user_id,
            cmd: 'create'
        }
    }).then((response) => {

    }).catch((error) => {
        console.log(error);
    })
}


function toggleReadMoreButtonSimple(element) {
    const contentContent = findAncestorWithClass(element, '.content-content');
    const readMore = findAncestorWithClass(element, '.read-more');
    const collapseContent = findAncestorWithClass(element, '.collapse-content');


    // const row = element.parentElement;
    // const contentContent = row.previousElementSibling.querySelector('.content-content');
    // const readMore = row.querySelector('.read-more');
    // const collapseContent = row.querySelector('.collapse-content');

    contentContent.style.maxHeight = 'none';
    readMore.style.display = 'none';
    collapseContent.style.display = '';
}


function toggleCollapseButton(element) {
    const contentContent = findAncestorWithClass(element, '.content-content');
    const readMore = findAncestorWithClass(element, '.read-more');
    const collapseContent = findAncestorWithClass(element, '.collapse-content');

    //
    // const row = element.parentElement;
    // const contentContent = row.previousElementSibling.querySelector('.content-content');
    // const readMore = row.querySelector('.read-more');
    // const collapseContent = row.querySelector('.collapse-content');

    contentContent.style.maxHeight = '5rem'; // 根据需要调整高度
    readMore.style.display = '';
    collapseContent.style.display = 'none';
}


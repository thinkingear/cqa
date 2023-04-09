function toggleContent(element) {
    const row = element.parentElement;
    const contentContent = row.previousElementSibling.querySelector('.content-content');
    const readMore = row.querySelector('.read-more');
    const collapseContent = row.querySelector('.collapse-content');

    if (contentContent.style.maxHeight === 'none') {
        contentContent.style.maxHeight = '3px'; // 根据需要调整高度
        readMore.style.display = '';
        collapseContent.style.display = 'none';
    } else {
        contentContent.style.maxHeight = 'none';
        readMore.style.display = 'none';
        collapseContent.style.display = '';
    }
}

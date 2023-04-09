function toggleContent(element) {
    const row = element.parentElement;
    const articleContent = row.previousElementSibling.querySelector('.article-content');
    const readMore = row.querySelector('.read-more');
    const collapseContent = row.querySelector('.collapse-content');

    if (articleContent.style.maxHeight === 'none') {
        articleContent.style.maxHeight = '3em'; // 根据需要调整高度
        readMore.style.display = '';
        collapseContent.style.display = 'none';
    } else {
        articleContent.style.maxHeight = 'none';
        readMore.style.display = 'none';
        collapseContent.style.display = '';
    }
}

function toggleCourseOverview(element) {
    const commentBox = findAncestorWithClass(element, '.comment-box');

    if (!commentBox) return;

    commentBox.style.display = 'none';

    const course_overview_content = document.querySelector('#course-overview-content');
    course_overview_content.style.display = 'block';
}

function toggleCommentBoxForCourseDetail(element) {
    const course_overview_content = document.querySelector('#course-overview-content');
    course_overview_content.style.display = 'none';

    const commentBox = findAncestorWithClass(element, '.comment-box');

    if (!commentBox) return;

    commentBox.style.display = 'block';
}


document.addEventListener('DOMContentLoaded', () => {
    const queryParams = new URLSearchParams(window.location.search);
    const video_id = queryParams.get('video');

    if (video_id === '') {
        return
    }

    const video_button = document.querySelector(`#video-${video_id}`);
    video_button.classList.add('active');
    const video_title = video_button.querySelector('div');
    video_title.innerHTML = '<i class="fa-solid fa-video"></i>' + video_title.innerHTML;

    const accordion_collapse = findAncestorWithClass(video_button, '.accordion-collapse');
    accordion_collapse.classList.add('show');
})





function toggleCommentBox(element) {
    const commentBox = findAncestorWithClass(element, '.comment-box')

    if (!commentBox) return;

    if (commentBox.style.display === 'none') {
        commentBox.style.display = 'block';
    } else {
        commentBox.style.display = 'none';
    }
}


function sendComment(element, content_type, content_id, poster_id) {
    const comment_feed = findAncestorWithClass(element, '.comment-feed-input')
    if (comment_feed.value === '') {
        return;
    }

    service.post(`/comment/`, {
        content_id: content_id,
        content_type: content_type,
        feed: comment_feed.value,
        poster_id: poster_id,
    }).then((response) => {
        console.log(response)
    }).catch((error) => {
        console.log(error)
    })

    comment_feed.value = ''
}

function toggleReplyForm(element) {
    const vote_reply = findAncestorWithClass(element, '.vote-reply');
    const reply_form = findAncestorWithClass(element, '.reply-form');
    vote_reply.classList.remove('d-flex')
    vote_reply.classList.add('d-none')
    reply_form.classList.remove('d-none')
    reply_form.classList.add('d-flex')
}

function toggleReplyCancel(element) {
    const vote_reply = findAncestorWithClass(element, '.vote-reply');
    const reply_form = findAncestorWithClass(element, '.reply-form');
    const reply_input = reply_form.querySelector('.reply-input');
    reply_input.value = '';

    vote_reply.classList.remove('d-none')
    vote_reply.classList.add('d-flex')
    reply_form.classList.remove('d-flex')
    reply_form.classList.add('d-none')
}

// content_type = ['questioncomment', 'answercomment', 'articlecomment', 'commentcomment']
function toggleReplyConfirm(element, content_type, content_id, poster_id) {
    const reply_form = findAncestorWithClass(element, '.reply-form');
    const reply_input = reply_form.querySelector('.reply-input');
    service.post(`/comment/`, {
        content_id: content_id,
        poster_id: poster_id,
        content_type: content_type,
        feed: reply_input.value,
    }).then((response) => {
        console.log(response)
    }).catch((error) => {
        console.log(error)
    })

    toggleReplyCancel(element)
}


document.addEventListener('DOMContentLoaded', () => {
    const replyInputs = document.querySelectorAll('.reply-input')
    replyInputs.forEach((replyInput) => {
        const replyConfirm = findAncestorWithClass(replyInput, '.reply-confirm')
        replyInput.addEventListener('input', () => {
            if (replyInput.value.trim().length > 0) {
                replyConfirm.removeAttribute('disabled')
            } else {
                replyConfirm.setAttribute('disabled', '')
            }
        })
    })
})


document.addEventListener('DOMContentLoaded', () => {
    const content_follow_buttons = document.querySelectorAll('.content-follow-button')
    content_follow_buttons.forEach((content_follow_button) => {
        const content_type = content_follow_button.dataset.contentType
        const content_id = content_follow_button.dataset.contentId
        const follower_id = content_follow_button.dataset.followerId
        const content_follow_button_text = content_follow_button.querySelector('.content-follow-button-text')

        let app_name = ''
        if (content_type === 'article') {
            app_name = 'pubedit'
        } else {
            app_name = 'qa'
        }

        service.get(`/${app_name}/${content_type}/follow/`, {
            params: {
                content_type: content_type,
                content_id: content_id,
                follower_id: follower_id,
            }
        }).then((response) => {
            const status = response.data.status
            if (status === 'followed') {
                content_follow_button.classList.remove('btn-light')
                content_follow_button.classList.add('btn-dark')
                content_follow_button_text.innerText = 'Following'
            }
        }).catch((error) => {

        })
    })
})


function toggleContentButton(element) {
    const content_type = element.dataset.contentType
    const content_id = element.dataset.contentId
    const follower_id = element.dataset.followerId

    let app_name = ''
    if (content_type === 'article') {
        app_name = 'pubedit'
    } else {
        app_name = 'qa'
    }

    let post_body = {
        content_type: content_type,
        content_id: content_id,
        follower_id: follower_id,
        cmd: '',
    }

    if (element.classList.contains('btn-light')) {
        post_body.cmd = 'follow'
    } else if (element.classList.contains('btn-dark')) {
        post_body.cmd = 'unfollow'
    }

    const content_follow_button_text = element.querySelector('.content-follow-button-text')
    const content_follow_button_num = element.querySelector('.content-follow-button-num')

    service.post(`/${app_name}/${content_type}/follow/`, post_body)
        .then((response) => {
            content_follow_button_num.innerText = response.data.count

            const status = response.data.status
            if (status === 'followed') {
                element.classList.remove('btn-light')
                element.classList.add('btn-dark')
                content_follow_button_text.innerText = 'Following'
            } else if (status === 'unfollowed') {
                element.classList.remove('btn-dark')
                element.classList.add('btn-light')
                content_follow_button_text.innerText = 'Follow'
            }
        }).catch((error) => {
            console.log(error)
    })
}


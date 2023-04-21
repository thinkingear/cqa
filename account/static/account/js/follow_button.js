function toggleFollowButton(element) {
    let cmd = ''
    if (element.innerText === ' FOLLOW') {
        cmd = "follow"
    } else if (element.innerText === ' FOLLOWING') {
        cmd = 'unfollow'
    }

    const followed_id = element.dataset.followedId
    const follower_id = element.dataset.followerId

    service.post('/account/follow/', {
        followed_id: followed_id,
        follower_id: follower_id,
        cmd: cmd,
    }).then((response) => {
        let status = response.data.status
        if (status === 'followed') {
            element.innerHTML = '<i class="fa-solid fa-user-check"></i> Following'
            element.classList.remove('btn-outline-primary')
            element.classList.add('btn-secondary')
        } else if (status === 'unfollowed') {
            element.innerHTML = '<i class="fa-solid fa-user-plus"></i> Follow'
            element.classList.remove('btn-secondary')
            element.classList.add('btn-outline-primary')
        }
    }).catch((error) => {

    })
}

document.addEventListener('DOMContentLoaded', () => {
    const follow_buttons = document.querySelectorAll('.follow-button')
    follow_buttons.forEach((follow_button) => {
        const followed_id = follow_button.dataset.followedId
        const follower_id = follow_button.dataset.followerId

        if (followed_id === follower_id) {
            follow_button.setAttribute('disabled', '')
            return
        }

        service.get('/account/follow/', {
            params: {
                followed_id: followed_id,
                follower_id: follower_id,
            }
        }).then((response) => {
            let status = response.data.status
            if (status === 'followed') {
                follow_button.innerHTML = '<i class="fa-solid fa-user-check"></i> Following'
                follow_button.classList.remove('btn-outline-primary')
                follow_button.classList.add('btn-secondary')
            } else if (status === 'unfollowed') {
                follow_button.innerHTML = '<i class="fa-solid fa-user-plus"></i> Follow'
                follow_button.classList.remove('btn-secondary')
                follow_button.classList.add('btn-outline-primary')
            } else if (status === 'error') {
                follow_button.innerHTML = '<i class="fa-solid fa-user-plus"></i> Follow'
                follow_button.classList.remove('btn-secondary')
                follow_button.classList.add('btn-outline-primary')
                follow_button.classList.add('disabled')
                console.log('user need to login')
            }
        }).catch((error) => {
            console.log(error)
        })
    })
})

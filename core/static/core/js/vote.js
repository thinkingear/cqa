document.addEventListener('DOMContentLoaded', () => {
    const vote_buttons = document.querySelectorAll('.vote-button')

    vote_buttons.forEach((vote_button) => {
        const upvote_button = vote_button.querySelector('.upvote-button')
        const downvote_button = vote_button.querySelector('.downvote-button')
        const vote_num_button = vote_button.querySelector('.vote-num')

        const content_type = vote_button.dataset.contentType
        const content_id = vote_button.dataset.contentId
        const user_id = vote_button.dataset.userId

        // console.log(`Content Type: ${content_type}, Content ID: ${content_id}, User ID: ${user_id}`)

        let vote_state = {
            upvoted: false,
            downvoted: false
        };

        service.get('/vote/', {
            params: {
                content_type: content_type,
                content_id: content_id,
                user_id: user_id,
            }
        }).then((response) => {
            let vote = response.data.vote
            if (vote === 1) {
                vote_state.upvoted = true
            } else if (vote === -1) {
                vote_state.downvoted = true
            }
        }).catch((error) => {
        }).finally(() => {
        });

        upvote_button.addEventListener('click', async () => {
            if (!vote_state.upvoted) {
                await service.post('/vote/', {
                    content_type: content_type,
                    content_id: content_id,
                    user_id: user_id,
                    vote: 1
                }).then((response) => {
                    vote_num_button.innerText = response.data.vote
                }).catch((error) => {

                });

                // Increment answer's vote count
                // Change upvote button icon color to blue
                vote_state.upvoted = true;

                if (vote_state.downvoted) {
                    // Decrement answer's vote count
                    // Change downvote button icon color back to normal
                    vote_state.downvoted = false;
                }
            } else {
                await service.post('/vote/', {
                    content_type: content_type,
                    content_id: content_id,
                    user_id: user_id,
                    vote: 0,
                }).then((response) => {
                    vote_num_button.innerText = response.data.vote
                }).catch((error) => {

                });

                // Decrement answer's vote count
                // Change upvote button icon color back to normal
                vote_state.upvoted = false;
            }
        });

        downvote_button.addEventListener('click', async () => {

            if (!vote_state.downvoted) {
                await service.post('/vote/', {
                    content_type: content_type,
                    content_id: content_id,
                    user_id: user_id,
                    vote: -1,
                }).then((response) => {
                    vote_num_button.innerText = response.data.vote
                }).catch((error) => {

                });

                // Decrement answer's vote count
                // Change downvote button icon color to red
                vote_state.downvoted = true;

                if (vote_state.upvoted) {
                    // Increment answer's vote count
                    // Change upvote button icon color back to normal
                    vote_state.upvoted = false;
                }
            } else {
                await service.post('/vote/', {
                    content_type: content_type,
                    content_id: content_id,
                    user_id: user_id,
                    vote: 0,
                }).then((response) => {
                    vote_num_button.innerText = response.data.vote
                }).catch((error) => {

                });

                // Increment answer's vote count
                // Change downvote button icon color back to normal
                vote_state.downvoted = false;
            }
        });
    })
})


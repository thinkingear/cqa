async function handleInputEvent(event) {
    const recipients_search_input = event.target;
    const invite_question_modal = findAncestorWithClass(recipients_search_input, '.invite-question-modal');
    const question_id = invite_question_modal.dataset.questionId;
    const invitor_id = invite_question_modal.dataset.invitorId;
    const recipient_username_query = event.target.value;

    const response = await service.get(`notification/invite/question/${question_id}/search/user/`, {
        params: {
            invitor_id: invitor_id,
            username_query: recipient_username_query,
        }
    });
    const recipients_data = response.data.recipients_data;

    const recipients_list = findAncestorWithClass(recipients_search_input, ".list-group");
    recipients_list.innerHTML = "";

    recipients_data.forEach((recipient_data) => {
        const list_item = document.createElement("li");
        list_item.classList.add("list-group-item", "px-3");

        let bio = "";
        if (recipient_data.bio !== "Add profile bio") {
            bio = `, ${recipient_data.bio}`;
        }

        let invite_button = "";
        if (recipient_data.is_invited) {
            invite_button =
                `<button type="button" class="btn btn-outline-primary disabled" data-mdb-ripple-color="dark">Invited
                 </button>`;
        } else {
            invite_button =
                `<button type="button" class="btn btn-outline-primary" data-mdb-ripple-color="dark" onclick="toggleInviteButton(this, '${recipient_data.invite_url}')">Invite
                 </button>`;
        }


        list_item.innerHTML =
            `           <div class="d-flex align-items-center my-1">
                            <!-- account avatar -->
                            <div class="col-md-1 me-2 recipient-avatar">
                                <a href="${recipient_data.profile_url}">
                                    <img src="${recipient_data.avatar}"
                                         alt="User profile picture"
                                         class="rounded-circle"
                                         width="40" height="40">
                                </a>
                            </div>
                            <!-- user info -->
                            <div class="col-md-8">
                                <!-- username, bio -->
                                <div class="recipient-usernaem"><a href="${recipient_data.profile_url}"><strong>@${recipient_data.username}</strong></a>${bio}</div>
                                <div class="recipients-follower-count" style="color: #939598;">${recipient_data.follower_num} followers</div>
                            </div>
                            <!-- Invite BUTTON -->
                            <div class="col-md-3 d-flex justify-content-end recipient-invite-button">
                                ${invite_button}
                            </div>
                        </div>
                    `;
        recipients_list.appendChild(list_item);
    });

}

document.addEventListener("DOMContentLoaded", () => {
    const modals = document.querySelectorAll(".invite-question-modal");

    modals.forEach((modal) => {
        modal.addEventListener("shown.bs.modal", () => {
            const recipients_search_input = modal.querySelector(".recipient-search-input");
            if (recipients_search_input) {
                recipients_search_input.addEventListener("input", handleInputEvent);
            }
        });

        modal.addEventListener("hidden.bs.modal", () => {
            const recipients_search_input = modal.querySelector(".recipient-search-input");
            if (recipients_search_input) {
                recipients_search_input.removeEventListener("input", handleInputEvent);
            }
        });
    });
});


async function toggleInviteButton(element, url) {
    const response = await service.get(url);
    if (response.data.status === "success") {
        const recipient_invite_button = findAncestorWithClass(element, ".recipient-invite-button");
        recipient_invite_button.innerHTML = `<button type="button" class="btn btn-outline-primary disabled" data-mdb-ripple-color="dark">Invited</button>`;
    }
}



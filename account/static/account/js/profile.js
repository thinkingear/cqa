const profileFilterForm = document.getElementById('profile-filter-form')
const profileContentTypeInputs = profileFilterForm.elements['profile-content-type']

function setProfileSelectedFilters() {
    const pathname = window.location.pathname;
    const pathComponents = pathname.split('/');

    if (pathComponents.length >= 6) {
        profileContentTypeInputs.value = pathComponents[4]
    }
}

document.addEventListener('DOMContentLoaded', setProfileSelectedFilters)

profileContentTypeInputs.forEach((profileContentTypeInput) => {
    profileContentTypeInput.addEventListener('change', profileUpdateFilters)
})

function profileUpdateFilters() {
    const selectedContentType = profileContentTypeInputs.value

    // 动态构建 baseUrl
    const protocol = window.location.protocol;
    const host = window.location.host;
    const pathname = window.location.pathname;
    const pathComponents = pathname.split('/');

    console.log(`pathname: ${pathname}`)

    if (pathComponents.length >= 6) {
        const userId = pathComponents[3];
        const baseUrl = `${protocol}//${host}/account/profile/${userId}`;
        window.location.href = baseUrl + '/' + selectedContentType + '/';
    } else {
        console.error('Invalid URL format');
    }
}

function displayProfileEditor(element, textareaId) {
    const profile_info = document.getElementById('profile-info')
    const user_id = profile_info.dataset.userId
    const request_user_id = profile_info.dataset.requestUserId

    if (user_id !== request_user_id) {
        return
    }

    const profile_content_old = element.getElementsByTagName('span')[0]
    const profile_editor = findAncestorWithClass(element, '.profile-editor')
    const profile_content_new = document.getElementById(textareaId)


    profile_content_new.value = profile_content_old.innerText
    element.style.display = 'none'
    profile_editor.style.display = 'block'
    profile_content_new.focus()
}

function hideProfileEditor(element, textareaId) {
    const profile_content_type = textareaId.split('-')[2];
    const profile_content = findAncestorWithClass(element, '.profile-content')
    const profile_content_old = profile_content.getElementsByTagName('span')[0]
    const profile_editor = findAncestorWithClass(element, '.profile-editor')
    const profile_info = document.getElementById('profile-info')

    const user_id = profile_info.dataset.userId

    if (profile_content_type === 'bio') {
        service.post(`/account/profile/${user_id}/bio/`, {
            bio: element.value
        }).then((response) => {
            profile_content_old.innerText = element.value
            profile_editor.style.display = 'none'
            profile_content.style.display = 'block'
        }).catch((error) => {
            console.log(error)
        })
    } else if (profile_content_type === 'description') {
        service.post(`/account/profile/${user_id}/description/`, {
            description: element.value
        }).then((response) => {
            profile_content_old.innerText = element.value
            profile_editor.style.display = 'none'
            profile_content.style.display = 'block'
        }).catch((error) => {
            console.log(error)
        })
    }
}



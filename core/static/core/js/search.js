// 获取筛选表单和表单元素
const searchFilterForm = document.getElementById('search-filter-form');
const searchContentTypeInputs = searchFilterForm.elements['search-content-type'];
const searchTimeInputs = searchFilterForm.elements['search-time'];

function setSeartchSelectedFilters() {
    const queryParams = new URLSearchParams(window.location.search);
    const selectedContentType = queryParams.get('type');
    const selectedTime = queryParams.get('time');

    if (selectedContentType) {
        searchFilterForm.elements['search-content-type'].value = selectedContentType;
    }
    if (selectedTime) {
        searchFilterForm.elements['search-time'].value = selectedTime;
    }
}

document.addEventListener('DOMContentLoaded', setSeartchSelectedFilters);


// 添加事件监听器
for (const input of searchContentTypeInputs) {
    input.addEventListener('change', updateSearchFilters);
}
for (const input of searchTimeInputs) {
    input.addEventListener('change', updateSearchFilters);
}

// 更新筛选条件
function updateSearchFilters() {
    const selectedContentType = searchContentTypeInputs.value;
    const selectedTime = searchTimeInputs.value;

    // 构建新的 URL
    const queryParams = new URLSearchParams(window.location.search);

    const queryType = queryParams.get('type')
    const queryTime = queryParams.get('time')

    if (queryType !== selectedContentType) {
        queryParams.set('type', selectedContentType)
    }

    if (queryTime !== selectedTime) {
        queryParams.set('time', selectedTime)
    }

    // 跳转到新的 URL
    window.location.href = `${window.location.pathname}?${queryParams.toString()}`;
}


function setSortedBy() {
    const queryParams = new URLSearchParams(window.location.search);

    if (queryParams.get('type') === 'course' && queryParams.get('sort') !== 'latest') {
        queryParams.set('sort', 'latest');
        window.location.href = `${window.location.pathname}?${queryParams.toString()}`;
        return;
    }

    const sortedByForm = document.querySelector("#sorted-by-form");

    sortedByForm.elements['sort-by'].value = queryParams.get('sort');
}

document.addEventListener('DOMContentLoaded', setSortedBy);

function updateSortedBy(element) {
    const sortedByForm = document.querySelector("#sorted-by-form");

    const sortedBy = sortedByForm.elements['sort-by'].value;

    const queryParams = new URLSearchParams(window.location.search);

    const querySortedBy = queryParams.get('sort');

    if (querySortedBy !== sortedBy) {
        queryParams.set('sort', sortedBy);
    }

    window.location.href = `${window.location.pathname}?${queryParams.toString()}`;
}

// submit-question
async function submit_question() {
    const questionInput = document.getElementById("question-input");
    const loadingSpinner = document.getElementById("loading-spinner");
    const responseMessage = document.getElementById("response-message");

    if (!questionInput.value.trim()) {
        responseMessage.innerHTML = '<div class="alert alert-danger">请输入问题。</div>';
        return;
    }

    responseMessage.innerHTML = '';
    loadingSpinner.classList.remove("d-none");

    try {
        const response = await service.post("/qa/question/ai/", {
            question: questionInput.value
        });

        if (response.data.status === "success") {
            responseMessage.innerHTML = `<div class="alert alert-success">A: ${response.data.answer}</div>`;
        } else {
            responseMessage.innerHTML = `<div class="alert alert-danger">Error：${response.data.message}</div>`;
        }
    } catch (error) {
        responseMessage.innerHTML = '<div class="alert alert-danger">Request failed</div>';
    } finally {
        loadingSpinner.classList.add("d-none");
    }
}


function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}

document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chatBox');
    const loadingSpinner = document.getElementById("loading-spinner");

    function createMessageBubble(content, sender) {
        const messageBubble = document.createElement('div');
        if (sender === 'ai') {
            messageBubble.classList.add("d-flex", "flex-row", "justify-content-start", "mb-4");
            messageBubble.innerHTML =
            `<div class="p-3 me-3" style="border-radius: 15px; background-color: rgba(57, 192, 237,.2);">
                <p class="small mb-0">${content}</p>
             </div>`
        } else {
            messageBubble.classList.add("d-flex", "flex-row", "justify-content-end", "mb-4");
            messageBubble.innerHTML =
            `<div class="p-3 ms-3 border" style="border-radius: 15px; background-color: #fbfbfb;">
                <p class="small mb-0">${content}</p>
             </div>`
        }



        return messageBubble;
    }


    document.getElementById('question-input-form').addEventListener('submit', function (e) {
        e.preventDefault();

        const question_input = document.getElementById('question-input').value.trim();

        if (question_input.length === 0) {
            return;
        }

        const questionBubble = createMessageBubble(question_input, 'user');
        chatBox.appendChild(questionBubble);

        loadingSpinner.classList.remove("d-none");


        service.post('/qa/question/ai/', {question: question_input})
            .then((response) => {
                if (response.data.status === 'success') {
                    const answer = response.data.answer;
                    const answerBubble = createMessageBubble(answer, 'ai');
                    chatBox.appendChild(answerBubble);
                }
            })
            .catch((error) => {
                console.log(error);
                const errorMessage = createMessageBubble('<strong>request failed</strong>', 'ai');
                chatBox.appendChild(errorMessage);
            })
            .finally(() => {
                loadingSpinner.classList.add("d-none");
            });

        scrollToBottom(chatBox);

        document.getElementById('question-input').value = '';
    });
});

function destroyAIAssistantRow() {
    const aiAssistantRow = document.querySelector('#ai-assistant-row');
    aiAssistantRow.remove();
}


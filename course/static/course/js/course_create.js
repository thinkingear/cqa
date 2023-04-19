function previewThumbnail(event) {
    const thumbnailInput = document.getElementById('thumbnail');
    const thumbnailPreview = document.getElementById('thumbnail_preview');
    if (thumbnailInput.files && thumbnailInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            thumbnailPreview.setAttribute('src', e.target.result);
            thumbnailPreview.style.display = 'block';
        }
        reader.readAsDataURL(thumbnailInput.files[0]);
    } else {
        thumbnailPreview.style.display = 'none';
    }
}

let section_sortable;
let video_sortables = new Map();
let section_counter = -1;
let section_counter_2_video_counter = new Map();

function createSectionSortable() {
    // 销毁并重新创建 Sortable 实例
    if (section_sortable) {
        section_sortable.destroy();
    }

    const el = document.querySelector("#section-table tbody");

    section_sortable = Sortable.create(el, {
        draggable: ".draggable-row",
        handle: ".drag-handle",
        animation: 150,
        onEnd: function (evt) {
            // 发送排序结果到服务器的逻辑
            const oldIndex = evt.oldIndex;
            const newIndex = evt.newIndex;
            console.log(`oldIndex = ${oldIndex}, newIndex = ${newIndex}`);
        },
    });
}

function createVideoSortable(section_id) {
    console.log(`section_id = ${section_id}`);
    const el = document.querySelector(`#${section_id} tbody`);

    let video_sortable = video_sortables.get(section_id);

    if (video_sortable) {
        video_sortable.destroy();
    }

    video_sortable = Sortable.create(el, {
        draggable: ".draggable-row",
        handle: ".drag-handle",
        animation: 150,
        onEnd: function (evt) {
            // 发送排序结果到服务器的逻辑
        },
    })

    video_sortables.set(section_id, video_sortable);
}

function addNewSection() {
    // Increment section counter
    ++section_counter;

    const sectionTable = document.getElementById("section-table");
    const section_id = "section_" + section_counter;
    video_sortables.set(section_id, null);

    const newRow = document.createElement("tr");
    newRow.classList.add("draggable-row");

    newRow.innerHTML = `
            <td><input onblur="updateModalTitle(this)" type="text" class="form-control" name="sections[${section_counter}].title" placeholder="section title" required/></td>
            <td><button type="button" class="btn btn-success btn-sm px-3" data-ripple-color="dark" data-mdb-toggle="modal" data-mdb-target="#${section_id}"><i class="fa-solid fa-plus"></i></button></td>
            <td><button onclick="deleteSection(this)" type="button" class="btn btn-danger btn-sm px-3" data-ripple-color="dark"><i class="fa-solid fa-trash-can"></i></button></td>
            <td><i class="fa-solid fa-sort drag-handle"></i></td>
        `;

    sectionTable.querySelector("tbody").appendChild(newRow);

    // 创建新的模态框
    const newModal = document.createElement("div");
    newModal.classList.add("modal", "fade");
    newModal.setAttribute("id", section_id);
    newModal.setAttribute("tabindex", "-1");
    newModal.setAttribute("aria-labelledby", section_id + "Label");
    newModal.setAttribute("aria-hidden", "true");

    newModal.innerHTML = `
  <div class="modal-dialog modal-xl">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="${section_id}Label">Section title</h5>
        <button type="button" class="btn btn-success ms-3" onclick="addNewVideo(this)">
        <i class="fa-solid fa-plus"></i>
        video
        </button>
        <button type="button" class="btn-close" data-mdb-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <table class="table align-middle mb-0 bg-white sortable video-table">
            <thead class="bg-light">
            <tr>
                <th>Title</th>
                <th>Description</th>
                <th>Video</th>
                <th>Delete</th>
                <th>Ordering</th>
            </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-mdb-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
  `;

    const course_form = document.querySelector('#course-form');
    course_form.appendChild(newModal);


    createSectionSortable();
}


function addNewVideo(add_video_button) {
    const video_modal = add_video_button.closest('.modal');
    const section_id = video_modal.getAttribute('id');
    const section_counter = parseInt(section_id.split('_')[1]);
    const video_table = video_modal.querySelector('.video-table');

    let video_counter = 0;
    if (section_counter_2_video_counter.has(section_counter)) {
        video_counter = section_counter_2_video_counter.get(section_counter) + 1;
        section_counter_2_video_counter.set(section_counter, video_counter);
    } else {
        section_counter_2_video_counter.set(section_counter, 0);
    }

    const newRow = document.createElement("tr");
    newRow.classList.add("draggable-row");

    newRow.innerHTML = `
        <td><input type="text" class="form-control" name="sections[${section_counter}].videos[${video_counter}].title" placeholder="video title" required></td>
        <td><textarea class="form-control" name="sections[${section_counter}].videos[${video_counter}].description" rows="1" placeholder="video description"></textarea></td>
        <td><input type="file" class="form-control" name="sections[${section_counter}].videos[${video_counter}].file" required></td>
        <td><button onclick="deleteVideo(this)" type="button" class="btn btn-danger btn-sm px-3" data-ripple-color="dark"><i class="fa-solid fa-trash-can"></i></button></td>
        <td><i class="fa-solid fa-sort drag-handle"></i></td>
    `;

    video_table.querySelector("tbody").appendChild(newRow);

    createVideoSortable(section_id);
}


function updateModalTitle(section_input) {
    const sectionRow = section_input.closest("tr");
    const add_button = sectionRow.querySelector('.btn-success');
    const modal_id = add_button.getAttribute('data-mdb-target');
    const video_modal = document.querySelector(modal_id);
    const video_modal_title = video_modal.querySelector('.modal-title');
    video_modal_title.innerText = section_input.value;
}

function deleteSection(delete_button) {
    const row = delete_button.closest("tr");

    const add_button = row.querySelector(".btn-success");
    const modalId = add_button.getAttribute("data-mdb-target");

    // 删除模态框
    const modal = document.querySelector(modalId);
    if (modal) {
        modal.remove();
    }

    row.remove();
    if (section_sortable) {
        section_sortable.save();
    }
}

function deleteVideo(delete_button) {
    const modal = delete_button.closest(".modal");
    const section_id = modal.getAttribute('id');
    const row = delete_button.closest("tr");
    row.remove();

    if (video_sortables.get(section_id)) {
        video_sortables.get(section_id).save();
    }
}



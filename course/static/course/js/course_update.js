// initialize section_counter & video_counter
document.addEventListener('DOMContentLoaded', () => {
    const section_table = document.querySelector('#section-table');
    section_counter = parseInt(section_table.getAttribute('data-initial-counter'));
    for (let sc = 0; sc <= section_counter; ++ sc) {
        const video_modal = document.querySelector(`#section_${sc}`);
        const video_counter = parseInt(video_modal.getAttribute("data-initial-counter"));
        section_counter_2_video_counter.set(sc, video_counter);
    }

    createSectionSortable();

    for (let sc = 0; sc <= section_counter; ++ sc) {
        const section_id = `section_${sc}`;
        createVideoSortable(section_id);
    }
})

function toggleDeleteCourseButton(element, course_id) {
    service.delete(`course/${course_id}/`
    ).then((response) => {
        window.location.reload()
    }).catch((error) => {
        console.log(error)
    })
}
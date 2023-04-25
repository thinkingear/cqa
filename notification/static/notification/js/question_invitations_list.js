document.addEventListener('DOMContentLoaded', function() {
    const dateHeadings = document.querySelectorAll('.invitation-date');
    let previousDate = null;

    dateHeadings.forEach((dateHeading) => {
        const currentDate = dateHeading.textContent;

        if (previousDate === currentDate) {
            dateHeading.remove();
        } else {
            previousDate = currentDate;
        }
    });
});
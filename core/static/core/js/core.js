/*
    params:
        className: e.g. '.comment-box' is valid, 'comment-box' is not
 */
function findAncestorWithClass(element, className) {
    while (element && !element.querySelector(className)) {
        element = element.parentElement;
    }

    if (!element) return null;
    return element.querySelector(className);
}
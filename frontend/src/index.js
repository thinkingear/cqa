import { renderMarkdown } from './markdown_display';
import 'highlight.js/styles/default.css';
import service  from "./request";

import 'easymde/dist/easymde.min.css';
import EasyMDE from 'easymde';

window.service = service;

document.addEventListener('DOMContentLoaded', () => {
  const textareas = document.getElementsByClassName('markdown-editor');

  for (let i = 0; i < textareas.length; i++) {
    new EasyMDE({ element: textareas[i] });
  }
});


document.addEventListener('DOMContentLoaded', () => {
  const markdownDataElements = document.getElementsByClassName('markdown-data');
  const renderedMarkdownElements = document.getElementsByClassName('rendered-markdown');

  for (let i = 0; i < markdownDataElements.length; i++) {
    const markdownText = markdownDataElements[i].innerHTML;
    const renderedMarkdown = renderMarkdown(markdownText);
    renderedMarkdownElements[i].innerHTML = renderedMarkdown;
  }
});




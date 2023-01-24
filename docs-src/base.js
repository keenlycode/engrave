import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';
import {
    addStyle,
    Badge
} from 'gadjet/src/gadjet';

hljs.registerLanguage('bash', bash);
hljs.highlightAll();

Badge.define('el-badge');

let _baseURL = new URL('./', document.currentScript.src);
let url = new URL('asset/fonts/FiraSans-Regular.ttf', _baseURL);

addStyle`
@font-face {
    font-family: 'sans';
    src: url('${url.toString()}') format('woff2');
}

html {
    font-family: sans;
    padding-bottom: 20vh;
    line-height: 1.7;
}

code {
    border-radius: 4px;
    background-color: #444;
    color: white;
    padding: 0.25rem;
}

.container {
    max-width: 1000px;
    min-width: 280px;
    width: 90%;
    margin: auto;
}
`
import 'packet-ui/dist/packet-ui.js';
import './_base.scss';
import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';
import 'highlight.js/styles/github.css';

hljs.registerLanguage('bash', bash);

hljs.highlightAll();
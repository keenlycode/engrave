import 'packet-ui/dist/packet-ui.js';
import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';

hljs.registerLanguage('bash', bash);
hljs.highlightAll();
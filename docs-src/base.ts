import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';
import { define } from 'gadjet/src/ui/ui';
import { Badge } from 'gadjet/src/ui/badge/badge';

hljs.registerLanguage('bash', bash);
hljs.highlightAll();

define('el-badge', Badge);

class Code extends HTMLElement {
    _lang: string;
    constructor() {
        super();
        this._lang = this.getAttribute("lang");
    }
}
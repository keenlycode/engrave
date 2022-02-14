import {define} from 'gadjet/src/ui/ui';
import {Badge} from 'gadjet/src/ui/badge/badge';
import hljs from 'highlight.js';
import bash from 'highlight.js/lib/languages/bash';
hljs.registerLanguage('bash', bash);

define('el-badge', Badge);

class Code extends HTMLElement {
    _lang: string;
    constructor() {
        super();
        this._lang = this.getAttribute("lang");
    }
}
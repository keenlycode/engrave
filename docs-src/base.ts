import { define, StyleClass, StyledElement } from 'gadjet/src/ui/ui';
import { Badge } from 'gadjet/src/ui/badge/badge';

import Prism from 'prismjs';
Prism;
// import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-django';

define('el-badge', Badge);


class Code extends StyledElement {

    _pre: boolean;
    _lang: string;
    _code: string;

    constructor() {
        super();
        if (this.hasAttribute('pre')) {
            this._pre = true;
        }
        this._lang = this.getAttribute('lang');
        this._code = this.childNodes[0].nodeValue;
        if (this.getAttribute('trim')) {
            this._code = this._code.trim();
        }
        this.render();
    }

    render() {
        this.innerText = '';
        let el: HTMLElement = document.createElement('code');
        el.append(this._code);
        el.classList.add(`language-${this._lang}`);
        if (this._pre) {
            let el_pre = document.createElement('pre');
            el_pre.classList.add(`language-${this._lang}`);
            el_pre.append(el);
            el = el_pre;
        }
        this.appendChild(el);
    }
}

define('el-code', Code);
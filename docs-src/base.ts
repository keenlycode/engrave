import { define } from 'gadjet/src/ui/ui';
import { Badge } from 'gadjet/src/ui/badge/badge';
import { html, render } from 'uhtml';

import Prism from 'prismjs';
import 'prismjs/components/prism-bash';

define('el-badge', Badge);

class Code extends HTMLElement {
    _lang: string;
    _innerHTML: string;
    constructor() {
        super();
        this._lang = this.getAttribute("lang");
        this._innerHTML = this.innerHTML;
        this.innerHTML = Prism.highlight(
            this._innerHTML,
            Prism.languages.bash,
            'javascript'
        )
    }
}
customElements.define('el-code', Code);
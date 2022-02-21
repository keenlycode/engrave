import { define } from 'gadjet/src/ui/ui';
import { Badge } from 'gadjet/src/ui/badge/badge';

import Prism from 'prismjs';
Prism;
import 'prismjs/components/prism-markup-templating';
import 'prismjs/components/prism-django';
import 'prismjs/plugins/line-numbers/prism-line-numbers';
import 'prismjs/plugins/line-highlight/prism-line-highlight';
import { addStyle } from 'gadjet/src/style';

define('el-badge', Badge);

addStyle`
pre[class*="language-"] {
    border: 0;
    margin-top: 0;
    border-top-left-radius: 0;
}
`
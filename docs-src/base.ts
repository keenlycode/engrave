import { define, StyleClass, StyledElement } from 'gadjet/src/ui/ui';
import { Badge } from 'gadjet/src/ui/badge/badge';

import Prism from 'prismjs';
Prism;
import 'prismjs/components/prism-markup-templating';
import 'prismjs/components/prism-django';
import 'prismjs/plugins/line-numbers/prism-line-numbers';
import 'prismjs/plugins/line-highlight/prism-line-highlight';

define('el-badge', Badge);
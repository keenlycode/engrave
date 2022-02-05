import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';
import {Badge} from 'gadjet/src/ui/badge/badge';
import {define} from 'gadjet/src/ui/ui';

hljs.registerLanguage('bash', bash);
hljs.highlightAll();

define('el-badge', Badge);
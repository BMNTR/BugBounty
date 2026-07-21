with open('C:/BugBounty/temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
js = re.sub(r"document\.getElementById\('labUrl'\)\.textContent = https://0a8f000- \+ id \+ \.web-security-academy\.net \+ def\.url;", 
            "document.getElementById('labUrl').textContent = `https://0a8f000-${id}.web-security-academy.net${def.url}`;", js)

with open('C:/BugBounty/temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
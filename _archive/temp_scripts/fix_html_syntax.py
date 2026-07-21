with open('C:/BugBounty/bugbounty_tutorial.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
html = re.sub(r"document\.getElementById\('labUrl'\)\.textContent = https://0a8f000- \+ id \+ \.web-security-academy\.net \+ def\.url;", 
            "document.getElementById('labUrl').textContent = `https://0a8f000-${id}.web-security-academy.net${def.url}`;", html)

with open('C:/BugBounty/bugbounty_tutorial.html', 'w', encoding='utf-8') as f:
    f.write(html)
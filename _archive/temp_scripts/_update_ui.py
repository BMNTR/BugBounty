import re

# Update components.js
with open("C:/BugBounty/js/components.js", "r", encoding="utf-8") as f:
    js = f.read()

header_new = """    renderHeader(data) {
        const container = el('div', 'topic-header');
        container.innerHTML = `
            <h1 style="font-size: 42px; font-family: var(--font-display); margin-bottom: 16px; letter-spacing:-0.02em; color:var(--text); border:none; padding:0">${data.title}</h1>
            <p style="font-size: 18px; color: var(--text2); max-width: 800px; margin-bottom: 24px; line-height: 1.6">${data.description}</p>
            <div style="display:flex; gap:12px; flex-wrap:wrap">
                <span style="background:var(--bg2); border:1px solid var(--border); padding:6px 12px; border-radius:6px; font-size:12px; font-weight:600; font-family:var(--font-mono); color:var(--accent)">OWASP ${data.owasp || '-'}</span>
                <span style="background:var(--bg2); border:1px solid var(--border); padding:6px 12px; border-radius:6px; font-size:12px; font-weight:600; font-family:var(--font-mono); color:var(--green)">${data.difficulty || '-'}</span>
                <span style="background:var(--bg2); border:1px solid var(--border); padding:6px 12px; border-radius:6px; font-size:12px; font-weight:600; font-family:var(--font-mono); color:var(--text2)">${data.estimatedTime || '-'}</span>
            </div>
        `;
        return container;
    },"""

js = re.sub(r'    renderHeader\(data\) \{[\s\S]*?return container;\n    \},', header_new, js)

demo_new = """    renderInteractiveDemo(data) {
        const container = el('div', 'content-section interactive-demo');
        const id = 'demo_input_' + Math.random().toString(36).substring(7);
        const queryId = 'demo_query_' + Math.random().toString(36).substring(7);
        const dbId = 'demo_db_' + Math.random().toString(36).substring(7);
        const statusId = 'demo_status_' + Math.random().toString(36).substring(7);
        
        container.style.padding = '0';
        container.style.background = 'var(--bg)';
        
        container.innerHTML = `
            <div style="padding:24px; border-bottom:1px solid var(--border)">
                <h3 style="border-bottom:none; margin:0 0 8px">Interactive Playground</h3>
                <p style="margin:0; font-size:14px">${data.description}</p>
            </div>
            <div style="padding:32px; display:flex; flex-direction:column; align-items:center; gap:24px; background:var(--bg2); border-radius: 0 0 12px 12px">
                <div style="background:var(--bg); border:1px solid var(--border); padding:16px 24px; border-radius:8px; width:100%; max-width:500px; box-shadow:var(--shadow)">
                    <div style="font-family:var(--font-mono); font-size:12px; color:var(--text3); margin-bottom:12px; display:flex; align-items:center; gap:8px">
                        Simulated Browser Input
                    </div>
                    <input type="text" id="${id}" value="${data.defaultInput}" style="width:100%; background:var(--bg2); color:var(--text); border:1px solid var(--border); padding:10px; border-radius:6px; font-family:var(--font-mono); font-size:14px; outline:none" />
                </div>
                <div style="color:var(--text3)">↓</div>
                <div style="background:var(--code-bg); border:1px solid var(--border); padding:20px; border-radius:8px; width:100%; box-shadow:var(--shadow)">
                    <div style="font-family:var(--font-mono); font-size:12px; color:var(--text3); margin-bottom:12px; display:flex; align-items:center; gap:8px">
                        Backend Server (Generated SQL)
                    </div>
                    <div class="live-query" id="${queryId}" style="font-size:16px; word-break:break-all"></div>
                </div>
                <div style="color:var(--text3)">↓</div>
                <div id="${dbId}" style="background:var(--bg); border:1px solid var(--border); padding:16px 24px; border-radius:8px; width:100%; max-width:500px; transition:all 0.3s">
                    <div style="font-family:var(--font-mono); font-size:12px; color:var(--text3); margin-bottom:8px; display:flex; align-items:center; gap:8px">
                        Database Execution
                    </div>
                    <div id="${statusId}" style="font-family:var(--font-mono); font-weight:bold; font-size:14px; color:var(--text2)">Status: Normal Execution</div>
                </div>
            </div>
        `;
        
        container.dataset.demoInput = id;
        container.dataset.demoQuery = queryId;
        container.dataset.demoDb = dbId;
        container.dataset.demoStatus = statusId;
        container.dataset.demoTemplate = data.template;
        return container;
    },"""

js = re.sub(r'    renderInteractiveDemo\(data\) \{[\s\S]*?return container;\n    \},', demo_new, js)


lab_new = """    renderLab(data) {
        const container = el('div', 'content-section');
        container.style.background = 'var(--code-bg)';
        container.style.border = '1px solid var(--border)';
        container.style.borderRadius = '12px';
        container.style.padding = '40px';
        container.style.margin = '0';
        container.style.position = 'relative';
        container.style.overflow = 'hidden';
        
        container.innerHTML = `
            <div style="position:absolute; top:0; left:0; width:4px; height:100%; background:var(--accent)"></div>
            <div style="font-family: var(--font-mono); font-size: 13px; color: var(--accent); margin-bottom: 16px; text-transform:uppercase; font-weight:bold; letter-spacing: 0.1em">LABORATORY</div>
            <h2 style="border:none; margin:0 0 16px; padding:0; font-size:28px">${data.title}</h2>
            <div style="display:flex; gap:16px; margin-bottom: 24px; font-family:var(--font-mono); font-size:13px">
                <span style="color:var(--text3)">Difficulty: <span style="color:var(--green)">${data.difficulty}</span></span>
                <span style="color:var(--text3)">Status: <span id="lab_status_${data.id}" style="color:var(--text2)">Unsolved</span></span>
            </div>
            <div style="background:var(--bg2); padding:20px; border-radius:8px; border:1px solid var(--border); margin-bottom: 32px">
                <p style="margin:0; font-size:15px"><strong>Objective:</strong> ${data.objective}</p>
            </div>
            <div style="display:flex; gap:16px">
                <button class="nav-btn primary" style="font-size:16px; padding:12px 32px; background:var(--accent); color:#000; border-radius:8px; font-weight:bold" onclick="startLab('${data.id}', '${data.url}')">ACCESS LAB</button>
                <button class="nav-btn" style="font-size:14px; padding:12px 32px; border-radius:8px" onclick="alert('${data.hint.replace(/'/g, "\\'")}')">View Hint</button>
            </div>
        `;
        return container;
    },"""
    
js = re.sub(r'    renderLab\(data\) \{[\s\S]*?return container;\n    \},', lab_new, js)

with open("C:/BugBounty/js/components.js", "w", encoding="utf-8") as f:
    f.write(js)

# Update engine.js
with open("C:/BugBounty/js/engine.js", "r", encoding="utf-8") as f:
    ejs = f.read()

engine_demo_old = """                if (sectionData.type === 'demo') {
                    const inputEl = document.getElementById(el.dataset.demoInput);
                    const queryEl = document.getElementById(el.dataset.demoQuery);
                    const template = el.dataset.demoTemplate;
                    
                    if (inputEl && queryEl && template) {
                        const updateQuery = () => {
                            const val = inputEl.value;
                            const highlighted = `<span class="live-input-val">${val}</span>`;
                            queryEl.innerHTML = template.replace('{input}', highlighted);
                        };
                        inputEl.addEventListener('input', updateQuery);
                        updateQuery();
                    }
                }"""
                
engine_demo_new = """                if (sectionData.type === 'demo') {
                    const inputEl = document.getElementById(el.dataset.demoInput);
                    const queryEl = document.getElementById(el.dataset.demoQuery);
                    const dbEl = document.getElementById(el.dataset.demoDb);
                    const statusEl = document.getElementById(el.dataset.demoStatus);
                    const template = el.dataset.demoTemplate;
                    
                    if (inputEl && queryEl && template) {
                        const updateQuery = () => {
                            const val = inputEl.value;
                            const highlighted = `<span class="live-input-val">${val}</span>`;
                            queryEl.innerHTML = template.replace('{input}', highlighted);
                            
                            if (val.includes("' OR") || val.includes("'--") || val.includes("' #")) {
                                dbEl.style.borderColor = "var(--red)";
                                dbEl.style.background = "rgba(239,68,68,0.1)";
                                statusEl.innerHTML = "Status: <span style='color:var(--red)'>BYPASSED / EXPLOITED</span>";
                            } else {
                                dbEl.style.borderColor = "var(--border)";
                                dbEl.style.background = "var(--bg)";
                                statusEl.innerHTML = "Status: <span style='color:var(--green)'>Normal / Safe</span>";
                            }
                        };
                        inputEl.addEventListener('input', updateQuery);
                        updateQuery();
                    }
                }"""

ejs = ejs.replace(engine_demo_old, engine_demo_new)

with open("C:/BugBounty/js/engine.js", "w", encoding="utf-8") as f:
    f.write(ejs)

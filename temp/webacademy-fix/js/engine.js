const ENGINE = {
    topicsList: [
        { id: 'sqli', title: '1. SQL Injection' },
        { id: 'xss', title: '2. Cross-Site Scripting' },
        { id: 'csrf', title: '3. CSRF' },
        { id: 'os-command', title: '4. OS Command Injection' },
        { id: 'ssrf', title: '5. SSRF' },
        { id: 'auth', title: '6. Authentication Bypass' },
        { id: 'path-traversal', title: '7. Path Traversal' },
        { id: 'idor', title: '8. IDOR' },
        { id: 'info-disc', title: '9. Info Disclosure' },
        { id: 'file-upload', title: '10. File Upload' }
    ],
    
    currentTopicIndex: 0,
    currentTopicData: null,
    
    // TOC State
    sectionsRendered: [],

    init() {
        this.renderSidebar();
        
        // Listen to scroll inside .main for Scrollspy
        const mainEl = document.getElementById('mainWrapper');
        if (mainEl) {
            mainEl.addEventListener('scroll', () => this.handleScrollspy());
        }

        // Load first topic by default or from hash
        const hash = window.location.hash.replace('#', '');
        const target = this.topicsList.find(t => t.id === hash) ? hash : 'sqli';
        this.loadTopic(target);
    },

    renderSidebar() {
        const nav = document.getElementById('sidebarNav');
        nav.innerHTML = '';
        this.topicsList.forEach(t => {
            const a = document.createElement('a');
            a.href = '#' + t.id;
            a.textContent = t.title;
            a.onclick = (e) => {
                e.preventDefault();
                window.location.hash = t.id;
                this.loadTopic(t.id);
            };
            a.id = 'nav_' + t.id;
            nav.appendChild(a);
        });
        
        // Update global progress
        document.getElementById('globalProgressText').textContent = `${window.storage.getSolvedLabsCount()} / ${this.topicsList.length} Labs`;
        document.getElementById('globalProgressFill').style.width = (window.storage.getSolvedLabsCount() / this.topicsList.length) * 100 + '%';
    },

    async loadTopic(topicId) {
        this.currentTopicIndex = this.topicsList.findIndex(t => t.id === topicId);
        document.getElementById('topbarCurrent').textContent = this.topicsList[this.currentTopicIndex].title;
        
        // Update sidebar active state
        document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
        const navEl = document.getElementById('nav_' + topicId);
        if (navEl) navEl.classList.add('active');

        // Clear content
        const container = document.getElementById('mainContent');
        container.innerHTML = '<div style="text-align:center; padding: 48px; color:var(--text3); grid-column: 1 / -1">Memuat materi...</div>';
        
        const mainWrapper = document.getElementById('mainWrapper');
        if(mainWrapper) mainWrapper.scrollTop = 0;

        try {
            const response = await fetch(`data/topics/${topicId}.json`);
            if (!response.ok) throw new Error('Network response was not ok');
            this.currentTopicData = await response.json();
            
            this.renderAllSections();
            this.renderTOC();
            
        } catch (error) {
            const topic = this.topicsList[this.currentTopicIndex];
            container.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1">
                    <div class="empty-state-icon">🚧</div>
                    <h3>${topic ? topic.title : 'Materi ini'} belum tersedia</h3>
                    <p>Kami masih menyiapkan materi untuk topik ini. Coba salah satu topik lain dulu, ya.</p>
                </div>`;
            const tocSidebar = document.getElementById('tocSidebar');
            if (tocSidebar) tocSidebar.innerHTML = '';
        }
    },

    renderAllSections() {
        const container = document.getElementById('mainContent');
        container.innerHTML = ''; // clear loading
        this.sectionsRendered = [];
        
        if (!this.currentTopicData || !this.currentTopicData.sections) return;

        this.currentTopicData.sections.forEach((sectionData, index) => {
            let el = null;
            let title = "Section";
            let widthClass = "span-half"; // default 1 column

            // Factory mapping based on section type
            switch (sectionData.type) {
                case 'header': 
                    el = UI.renderHeader(sectionData.data); 
                    title = "Header & Info"; 
                    widthClass = "span-full"; 
                    break;
                case 'objectives': 
                    el = UI.renderLearningObjectives(sectionData.data); 
                    title = "Learning Objectives"; 
                    break;
                case 'theory': 
                    el = UI.renderTheory(sectionData.data); 
                    title = sectionData.data.title || "Konsep Dasar"; 
                    break;
                case 'flow': 
                    el = UI.renderFlowDiagram(sectionData.data); 
                    title = sectionData.data.title || "Bagaimana Terjadi"; 
                    break;
                case 'visual': 
                    el = UI.renderVisualExplanation(sectionData.data); 
                    title = "Penjelasan Visual"; 
                    break;
                case 'impact': 
                    el = UI.renderImpact(sectionData.data); 
                    title = "Dampak"; 
                    break;
                case 'mitigation': 
                    el = UI.renderMitigation(sectionData.data); 
                    title = "Cara Mencegah"; 
                    break;
                case 'demo': 
                    el = UI.renderInteractiveDemo(sectionData.data); 
                    title = "Interactive Demo"; 
                    widthClass = "span-full"; 
                    break;
                case 'lab': 
                    el = UI.renderLab(sectionData.data); 
                    title = "Lab Praktik"; 
                    widthClass = "span-full"; 
                    break;
                case 'afterlab': 
                    el = UI.renderAfterLab(sectionData.data); 
                    title = "Setelah Lab"; 
                    break;
                case 'summary': 
                    el = UI.renderSummary(sectionData.data); 
                    title = "Ringkasan"; 
                    break;
                case 'quiz': 
                    el = UI.renderQuiz(sectionData.data); 
                    title = "Kuis Interaktif"; 
                    widthClass = "span-full";
                    break;
                case 'references': 
                    el = UI.renderReferences(sectionData.data); 
                    title = "Referensi"; 
                    widthClass = "span-full"; 
                    break;
            }

            if (el) {
                // Add grid sizing class
                el.classList.add(widthClass);
                el.id = 'section-' + index;
                
                // Track for Scrollspy & TOC
                this.sectionsRendered.push({
                    id: el.id,
                    title: title,
                    element: el,
                    index: index
                });

                container.appendChild(el);

                // Bind Demo events if it's a demo
                if (sectionData.type === 'demo') {
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
                }
                
                // Check Lab status
                if (sectionData.type === 'lab') {
                    const labId = sectionData.data.id;
                    const statusEl = document.getElementById('lab_status_' + labId);
                    if (window.storage.isLabSolved(labId) && statusEl) {
                        statusEl.textContent = 'Solved';
                        statusEl.style.color = 'var(--green)';
                    }
                }
            }
        });
        
        // Ensure mark as read for full topic since there's no more progressive disclosure
        window.storage.markSectionRead(this.currentTopicData.id, this.currentTopicData.sections.length);
    },

    renderTOC() {
        const tocSidebar = document.getElementById('tocSidebar');
        if (!tocSidebar) return;
        
        let headerData = null;
        let labData = null;
        
        if (this.currentTopicData && this.currentTopicData.sections) {
            this.currentTopicData.sections.forEach(s => {
                if (s.type === 'header') headerData = s.data;
                if (s.type === 'lab') labData = s.data;
            });
        }
        
        let html = '';
        
        if (headerData) {
            html += `
            <div class="toc-header" style="border-bottom:none; margin-bottom:0">Topic Overview</div>
            <div style="background:var(--bg2); border:1px solid var(--border); padding:16px; border-radius:12px; margin-bottom:24px; font-size:13px; font-family:var(--font-mono)">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px">
                    <span style="color:var(--text3)">Difficulty</span>
                    <strong style="color:var(--green)">${headerData.difficulty || '-'}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px">
                    <span style="color:var(--text3)">Time</span>
                    <strong>${headerData.estimatedTime || '-'}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px">
                    <span style="color:var(--text3)">XP Reward</span>
                    <strong style="color:var(--accent)">${headerData.reward || '-'}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px">
                    <span style="color:var(--text3)">OWASP</span>
                    <strong>${headerData.owasp || '-'}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:16px">
                    <span style="color:var(--text3)">Prerequisite</span>
                    <strong>${headerData.prerequisite || '-'}</strong>
                </div>
                
                ${labData ? `<button class="nav-btn primary" style="width:100%; text-align:center" onclick="startLab('${labData.id}', '${labData.url}')">Start Lab</button>` : ''}
            </div>
            `;
        }
        
        html += `
        <div class="toc-header">Daftar Materi</div>
        <ul class="toc-list" id="tocList"></ul>
        <div class="toc-progress-box">
          <div style="font-size:12px;color:var(--text3);margin-bottom:8px;font-family:var(--font-mono)">Progress Materi</div>
          <div class="progress-container"><div class="progress-fill" id="topicProgressFill" style="width:0%"></div></div>
        </div>
        `;
        
        tocSidebar.innerHTML = html;
        
        const tocList = document.getElementById('tocList');
        
        this.sectionsRendered.forEach((sec, idx) => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#' + sec.id;
            a.id = 'toc-' + sec.id;
            a.innerHTML = `<span style="width:20px;display:inline-block">${idx + 1}.</span> <span style="flex:1">${sec.title}</span> <div class="status-dot"></div>`;
            
            a.onclick = (e) => {
                e.preventDefault();
                sec.element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            };
            
            li.appendChild(a);
            tocList.appendChild(li);
        });
        
        this.handleScrollspy(); // Initial state
    },

    handleScrollspy() {
        if (this.sectionsRendered.length === 0) return;
        
        const mainEl = document.getElementById('mainWrapper');
        if (!mainEl) return;
        
        const scrollTop = mainEl.scrollTop;
        const mainHeight = mainEl.clientHeight;
        const scrollBottom = scrollTop + mainHeight;
        
        let activeIndex = 0;
        let highestVisibleIndex = 0;

        this.sectionsRendered.forEach((sec, i) => {
            const el = sec.element;
            const top = el.offsetTop - 100; // offset for sticky header
            if (scrollTop >= top) {
                activeIndex = i;
            }
            // Mark as completed/visible if user scrolled past it
            const elBottom = el.offsetTop + el.offsetHeight;
            if (scrollTop + (mainHeight / 2) > el.offsetTop) {
                highestVisibleIndex = Math.max(highestVisibleIndex, i);
            }
        });

        // Update active class in TOC
        this.sectionsRendered.forEach((sec, i) => {
            const tocA = document.getElementById('toc-' + sec.id);
            if (tocA) {
                if (i === activeIndex) {
                    tocA.classList.add('active');
                } else {
                    tocA.classList.remove('active');
                }
                
                if (i <= highestVisibleIndex) {
                    tocA.classList.add('completed');
                } else {
                    tocA.classList.remove('completed');
                }
            }
        });
        
        // Update Topic Progress Box
        const progressPercent = ((highestVisibleIndex + 1) / this.sectionsRendered.length) * 100;
        const fillEl = document.getElementById('topicProgressFill');
        if (fillEl) {
            fillEl.style.width = progressPercent + '%';
        }
    },

    checkQuizAnswer(btn, qIdx, optIdx, correctIdx, explanation) {
        const allOpts = btn.parentElement.querySelectorAll('.quiz-opt');
        allOpts.forEach(o => { o.disabled = true; o.style.opacity = 0.7; });
        
        const resultBox = btn.parentElement.parentElement.querySelector('.quiz-result');
        
        if (optIdx === correctIdx) {
            btn.classList.add('correct');
            resultBox.innerHTML = `<strong>Jawaban Benar!</strong><br>${explanation}`;
            resultBox.className = 'quiz-result ok show';
        } else {
            btn.classList.add('wrong');
            allOpts[correctIdx].classList.add('correct');
            resultBox.innerHTML = `<strong>Jawaban Kurang Tepat.</strong><br>${explanation}`;
            resultBox.className = 'quiz-result bad show';
        }
    }
};

window.engine = ENGINE;

// Init on load
document.addEventListener('DOMContentLoaded', () => {
    window.engine.init();
});

// THEME: toggles the `.light` class on <html> and remembers the choice.
// (Applied on load via an inline script in <head> too, to avoid a flash of the wrong theme.)
function toggleTheme() {
    const isLight = document.documentElement.classList.toggle('light');
    localStorage.setItem('wsa_theme', isLight ? 'light' : 'dark');
}

// SIDEBAR: on desktop this collapses the sidebar column to reclaim reading width;
// on mobile (<=900px) it opens/closes the sidebar as an overlay drawer.
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    const isMobile = window.innerWidth <= 900;

    if (isMobile) {
        const open = sidebar.classList.toggle('mobile-open');
        if (backdrop) backdrop.classList.toggle('active', open);
    } else {
        const collapsed = document.querySelector('.layout-wrapper').classList.toggle('sidebar-collapsed');
        localStorage.setItem('wsa_sidebar_collapsed', collapsed ? '1' : '0');
    }
}

// Restore desktop sidebar collapse state, and auto-close the mobile drawer
// (and its backdrop) whenever the viewport is resized back up to desktop width.
if (window.innerWidth > 900 && localStorage.getItem('wsa_sidebar_collapsed') === '1') {
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelector('.layout-wrapper').classList.add('sidebar-collapsed');
    });
}
window.addEventListener('resize', () => {
    if (window.innerWidth > 900) {
        const sidebar = document.getElementById('sidebar');
        const backdrop = document.getElementById('sidebarBackdrop');
        if (sidebar) sidebar.classList.remove('mobile-open');
        if (backdrop) backdrop.classList.remove('active');
    }
});

// Close the mobile drawer automatically after picking a topic, for a native app feel.
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('sidebarNav').addEventListener('click', (e) => {
        if (e.target.tagName === 'A' && window.innerWidth <= 900) {
            document.getElementById('sidebar').classList.remove('mobile-open');
            const backdrop = document.getElementById('sidebarBackdrop');
            if (backdrop) backdrop.classList.remove('active');
        }
    });
});

function startLab(labId, url) {
    const modal = document.getElementById('labModal');
    const iframeBox = document.getElementById('labContent');
    const urlBox = document.getElementById('labUrl');
    
    urlBox.textContent = url;
    
    if (labId === 'lab-sqli-01') {
        iframeBox.innerHTML = `
            <div style="padding:40px; color:var(--text); font-family:var(--font-main); height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; background:var(--bg)">
                <div style="background:var(--bg2); padding:32px; border-radius:12px; width:100%; max-width:400px; border:1px solid var(--border); box-shadow:var(--shadow)">
                    <h2 style="margin-top:0; border-bottom:1px solid var(--border); padding-bottom:16px; margin-bottom:24px; font-family:var(--font-display)">Admin Login</h2>
                    <div style="margin-bottom:16px; text-align:left">
                        <label style="display:block; margin-bottom:8px; color:var(--text2); font-family:var(--font-mono); font-size:12px">USERNAME</label>
                        <input type="text" id="labUsername" style="width:100%; padding:10px; background:var(--bg); border:1px solid var(--border); border-radius:6px; color:var(--text); outline:none; font-family:var(--font-mono)">
                    </div>
                    <div style="margin-bottom:24px; text-align:left">
                        <label style="display:block; margin-bottom:8px; color:var(--text2); font-family:var(--font-mono); font-size:12px">PASSWORD</label>
                        <input type="password" id="labPassword" style="width:100%; padding:10px; background:var(--bg); border:1px solid var(--border); border-radius:6px; color:var(--text); outline:none; font-family:var(--font-mono)">
                    </div>
                    <button onclick="checkLabLogin('${labId}')" style="width:100%; padding:12px; background:var(--accent); color:#000; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-family:var(--font-display)">LOGIN</button>
                    <div id="labResult" style="margin-top:16px; text-align:center; font-family:var(--font-mono); font-size:13px"></div>
                </div>
            </div>
        `;
        window.checkLabLogin = function(id) {
            const user = document.getElementById('labUsername').value;
            const res = document.getElementById('labResult');
            if (user.includes("' OR") || user.includes("'--") || user.includes("' #")) {
                res.style.color = 'var(--green)';
                res.innerHTML = "Success! Authentication bypassed.<br><button onclick='completeLab(\"" + id + "\")' style='margin-top:16px; padding:10px 20px; background:var(--green); color:#000; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-family:var(--font-display)'>CLAIM REWARD</button>";
            } else {
                res.style.color = 'var(--red)';
                res.textContent = "Invalid username or password.";
            }
        };
    } else {
        iframeBox.innerHTML = `<div style="padding:40px; text-align:center; color:var(--text2); font-family:var(--font-mono)">Lab environment currently unavailable.</div>`;
    }
    
    modal.classList.add('active');
}

function completeLab(labId) {
    window.storage.markLabSolved(labId);
    alert('Lab Solved! +50 XP');
    closeLab();
    window.location.reload();
}

function closeLab() {
    document.getElementById('labModal').classList.remove('active');
    document.getElementById('labContent').innerHTML = '';
}

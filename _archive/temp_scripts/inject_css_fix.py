import re

with open("C:/BugBounty/bugbounty_tutorial.html", "r", encoding="utf-8") as f:
    html = f.read()

# Insert new CSS just before </style>
if "/* === NEW UX & DIAGRAM STYLES === */" not in html:
    html = html.replace("</style>", "\n" + """
/* === NEW UX & DIAGRAM STYLES === */
.reading-progress-container {
  position: fixed; top: 0; left: 0; width: 100%; height: 4px; background: transparent; z-index: 1000;
}
.reading-progress-bar {
  height: 100%; background: var(--accent); width: 0%; transition: width 0.1s;
}
.topic-header { margin-bottom: 48px; }
.topic-meta { display: flex; gap: 16px; margin-top: 16px; font-family: var(--font-mono); font-size: 13px; color: var(--text3); }
.topic-meta-item { display: flex; align-items: center; gap: 6px; background: var(--bg2); padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border); }
.content-section { margin-bottom: 64px; }
.content-section h3 { font-size: 24px; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 24px; color: var(--text); }
.content-section h4 { font-size: 18px; color: var(--text); margin-top: 32px; margin-bottom: 16px; }
.box-diagram { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 32px; background: var(--bg2); border-radius: 12px; border: 1px solid var(--border); margin: 32px 0; }
.diagram-node { background: var(--bg); border: 1px solid var(--border); padding: 16px 24px; border-radius: 8px; text-align: center; width: 100%; max-width: 400px; font-family: var(--mono); font-size: 14px; }
.diagram-arrow { color: var(--text3); font-size: 20px; line-height: 1; }
.grid-diagram { display: grid; grid-template-columns: 1fr auto 1fr; gap: 16px; align-items: center; background: var(--bg2); padding: 32px; border-radius: 12px; border: 1px solid var(--border); margin: 32px 0; }
.nav-buttons { display: flex; justify-content: space-between; margin-top: 64px; padding-top: 32px; border-top: 1px solid var(--border); }
.nav-btn { background: var(--bg2); border: 1px solid var(--border); color: var(--text); padding: 12px 24px; border-radius: 8px; font-family: var(--font-display); cursor: pointer; transition: 0.2s; text-decoration: none; display: inline-block; }
.nav-btn:hover { background: var(--bg3); border-color: var(--text3); }
.nav-btn.primary { background: var(--text); color: var(--bg); border: none; }
.nav-btn.primary:hover { background: var(--text2); }
.interactive-demo { background: var(--code-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin: 32px 0; }
.interactive-demo input { width: 100%; background: var(--bg); color: var(--text); border: 1px solid var(--border); padding: 12px; border-radius: 6px; font-family: var(--mono); font-size: 14px; margin-bottom: 16px; }
.interactive-demo input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-dim); }
.live-query { color: #c586c0; font-family: var(--mono); font-size: 14px; line-height: 1.6; }
.live-input-val { color: #ce9178; font-weight: bold; background: rgba(206,145,120,0.1); padding: 2px 4px; border-radius: 4px; }
.section-card { background: var(--bg2); border: 1px solid var(--border); padding: 24px; border-radius: 12px; margin-bottom: 24px; }
.quiz-container { background: var(--bg2); border: 1px solid var(--border); padding: 32px; border-radius: 12px; margin-top: 32px; }
.quiz-question { margin-bottom: 24px; }
.quiz-question h4 { margin-top: 0; }
""" + "\n</style>")

with open("C:/BugBounty/bugbounty_tutorial.html", "w", encoding="utf-8") as f:
    f.write(html)
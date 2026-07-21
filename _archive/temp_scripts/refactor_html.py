import re

with open("C:/BugBounty/bugbounty_tutorial.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract styles
style_matches = re.findall(r'<style>(.*?)</style>', html, re.DOTALL)
css_content = "\n".join(style_matches)

# Extract scripts
script_matches = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
js_content = "\n".join(script_matches)

# Save to files
with open("C:/BugBounty/css/style.css", "w", encoding="utf-8") as f:
    f.write(css_content)

with open("C:/BugBounty/js/legacy.js", "w", encoding="utf-8") as f:
    f.write(js_content)

# Create the new shell HTML
shell_html = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bug Bounty: Web Security Academy</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
</head>
<body class="lang-id">
<div class="reading-progress-container"><div class="reading-progress-bar" id="readingProgress"></div></div>

<div class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <h2><span style="color:var(--accent)">//</span> Web Security Academy</h2>
  </div>
  <div style="padding: 16px 20px;">
    <div style="font-size: 12px; color: var(--text2); margin-bottom: 8px;">TOTAL PROGRESS</div>
    <div class="progress-container"><div class="progress-fill" id="globalProgressFill"></div></div>
    <div class="progress-text" id="globalProgressText">0 / 10 Labs</div>
  </div>
  <nav class="sidebar-nav" id="sidebarNav"></nav>
</div>

<main class="main">
  <div class="topbar">
    <button class="mobile-menu" id="mobileMenu" onclick="toggleSidebar()">&#9776;</button>
    <div class="topbar-page" id="topbarBreadcrumb">
      <span>Academy</span>
      <span class="sep">/</span>
      <strong class="cur" id="topbarCurrent">Dashboard</strong>
    </div>
    <div class="topbar-actions">
      <button class="lang-toggle-btn" onclick="toggleLanguage()">EN / ID</button>
      <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn" aria-label="Toggle Theme">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path></svg>
      </button>
    </div>
  </div>

  <!-- DYNAMIC CONTENT CONTAINER -->
  <div class="content" id="mainContent">
    <!-- Rendered by engine.js -->
  </div>
</main>

<div class="lab-modal" id="labModal">
  <div class="lab-window">
    <div class="lab-browser-bar">
      <div style="display:flex;gap:6px">
        <div style="width:12px;height:12px;border-radius:50%;background:#ef4444"></div>
        <div style="width:12px;height:12px;border-radius:50%;background:#f59e0b"></div>
        <div style="width:12px;height:12px;border-radius:50%;background:#10b981"></div>
      </div>
      <div class="lab-browser-url" id="labUrl">/</div>
      <div class="lab-browser-close" onclick="closeLab()">&times;</div>
    </div>
    <div class="lab-iframe-content" id="labContent"></div>
  </div>
</div>

<script src="js/storage.js"></script>
<script src="js/components.js"></script>
<script src="js/engine.js"></script>

<!-- Legacy scripts for now until fully refactored -->
<script src="js/legacy.js"></script>

</body>
</html>
"""

with open("C:/BugBounty/bugbounty_tutorial.html", "w", encoding="utf-8") as f:
    f.write(shell_html)

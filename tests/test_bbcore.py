"""Unit tests for BugBounty Orchestrator (bbcore) and workspace guards."""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from bbcore.orchestrator import slugify, ProgramState, Orchestrator
from bbcore.proxy_manager import ProxyManager, Proxy
from bbcore.skill_loader import SkillLoader
from bbcore.workflow_tools import check_asset


class TestSlugify(unittest.TestCase):
    def test_domain_slug(self):
        self.assertEqual(slugify("example.com"), "example-com")
        self.assertEqual(slugify("sub.example.com"), "sub-example-com")

    def test_url_slug(self):
        self.assertEqual(slugify("https://api.target.com/v1/users"), "api-target-com")
        self.assertEqual(slugify("http://target.com:8080/path"), "target-com")

    def test_special_chars(self):
        self.assertEqual(slugify("my_test_program"), "my-test-program")
        self.assertEqual(slugify("test---slug"), "test-slug")
        self.assertEqual(slugify(""), "program")


class TestProxyManager(unittest.TestCase):
    def setUp(self):
        self.pm = ProxyManager()

    def test_direct_mode(self):
        self.pm.mode = ProxyManager.MODE_DIRECT
        self.assertIsNone(self.pm.current)
        self.assertIsNone(self.pm.peek())
        self.assertEqual(self.pm.get_env(), {})
        self.assertEqual(self.pm.curl_args(), [])
        self.assertEqual(self.pm.status_text(), "Direct")

    def test_static_mode(self):
        self.pm.mode = ProxyManager.MODE_STATIC
        self.pm.static_proxy = self.pm._parse_proxy("http://127.0.0.1:8080")
        self.assertEqual(self.pm.mode, ProxyManager.MODE_STATIC)
        p = self.pm.peek()
        self.assertIsNotNone(p)
        self.assertEqual(p.host, "127.0.0.1")
        self.assertEqual(p.port, 8080)
        # Verify peek does not mutate or lose state
        self.assertEqual(self.pm.current.url, p.url)

    def test_peek_no_rotate(self):
        self.pm.mode = ProxyManager.MODE_ROTATE
        self.pm.proxy_list = [
            Proxy("http", "1.1.1.1", 8080),
            Proxy("http", "2.2.2.2", 8080),
        ]
        p1 = self.pm.peek()
        p2 = self.pm.peek()
        self.assertEqual(p1.host, p2.host)
        # Calling current rotates
        c1 = self.pm.current
        c2 = self.pm.current
        self.assertNotEqual(c1.host, c2.host)


class TestSkillLoader(unittest.TestCase):
    def setUp(self):
        self.loader = SkillLoader(bb_dir=ROOT_DIR)

    def test_skills_enumeration(self):
        skills = self.loader.list_available()
        self.assertGreaterEqual(len(skills), 75)
        self.assertIn("bbp-program-orchestrator", skills)
        self.assertIn("bbp-report-writer", skills)
        self.assertIn("bbp-rea-wrapper", skills)

    def test_load_skill_content(self):
        content = self.loader.load_skill("bbp-program-orchestrator")
        self.assertIsNotNone(content)
        self.assertIn("Program Workflow Orchestrator", content)


class TestScopeGuard(unittest.TestCase):
    def test_check_asset_in_scope(self):
        scope = {
            "in": ["*.target.com", "api.partner.org"],
            "out": ["admin.target.com", "out-of-scope.target.com"],
        }
        status, reason = check_asset(scope, "test.target.com")
        self.assertEqual(status, "IN")

        status, reason = check_asset(scope, "api.partner.org")
        self.assertEqual(status, "IN")

    def test_check_asset_out_of_scope(self):
        scope = {
            "in": ["*.target.com"],
            "out": ["admin.target.com"],
        }
        status, reason = check_asset(scope, "admin.target.com")
        self.assertEqual(status, "OUT")

    def test_check_asset_unknown(self):
        scope = {
            "in": ["target.com"],
            "out": [],
        }
        status, reason = check_asset(scope, "otherdomain.com")
        self.assertEqual(status, "UNKNOWN")


class TestOrchestratorStatus(unittest.TestCase):
    def test_status_structure(self):
        orc = Orchestrator()
        s = orc.status()
        self.assertIn("proxy_mode", s)
        self.assertIn("proxy_status", s)
        self.assertIn("available_skills", s)
        self.assertIn("programs", s)
        self.assertGreaterEqual(s["available_skills"], 75)


if __name__ == "__main__":
    unittest.main()

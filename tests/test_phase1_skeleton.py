"""一期骨架的静态检查。不依赖模拟器，也不导入 maa。"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "agent"
sys.path.insert(0, str(AGENT))

from cdk_auth import check_license  # noqa: E402


def _load_install():
    tools_dir = str(ROOT / "tools")
    sys.path.insert(0, tools_dir)
    spec = importlib.util.spec_from_file_location(
        "maatta_install", ROOT / "tools" / "install.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pipeline_nodes() -> dict[str, dict]:
    nodes: dict[str, dict] = {}
    pipeline = ROOT / "assets" / "resource" / "pipeline"
    for path in sorted(pipeline.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for name, node in data.items():
            if name in nodes:
                raise AssertionError(f"节点重名 {name}: {path}")
            if not isinstance(node, dict):
                raise AssertionError(f"{path} 里的 {name} 不是对象")
            nodes[name] = node
    return nodes


def _refs(value):
    if isinstance(value, str):
        name = value
        if name.startswith("[") and "]" in name:
            name = name.split("]", 1)[1]
        yield name
    elif isinstance(value, dict) and "name" in value:
        yield value["name"]
    elif isinstance(value, list):
        for item in value:
            yield from _refs(item)


def _templates(node: dict) -> list[str]:
    found = []

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "template":
                    if isinstance(item, str):
                        found.append(item)
                    elif isinstance(item, list):
                        found.extend(x for x in item if isinstance(x, str))
                else:
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(node)
    return found


class CdkAuthTests(unittest.TestCase):
    def setUp(self):
        self._saved = {
            key: os.environ.get(key) for key in ("MAATTA_CDK", "MAATTA_DEV_SKIP_CDK")
        }
        os.environ.pop("MAATTA_CDK", None)
        os.environ.pop("MAATTA_DEV_SKIP_CDK", None)

    def tearDown(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_default_dev_mode_passes_both_tiers(self):
        self.assertTrue(check_license("base"))
        self.assertTrue(check_license("activity"))

    def test_explicit_skip_passes_without_cdk(self):
        os.environ["MAATTA_DEV_SKIP_CDK"] = "yes"
        os.environ["MAATTA_CDK"] = ""
        self.assertTrue(check_license("base"))
        self.assertTrue(check_license("activity"))

    def test_strict_empty_cdk_fails(self):
        os.environ["MAATTA_DEV_SKIP_CDK"] = "0"
        self.assertFalse(check_license("base"))
        self.assertFalse(check_license("activity"))

    def test_strict_false_word_and_whitespace_cdk(self):
        os.environ["MAATTA_DEV_SKIP_CDK"] = "False"
        os.environ["MAATTA_CDK"] = "   "
        self.assertFalse(check_license("base"))

    def test_strict_nonempty_cdk_passes_without_server(self):
        os.environ["MAATTA_DEV_SKIP_CDK"] = "off"
        os.environ["MAATTA_CDK"] = "local-placeholder"
        self.assertTrue(check_license("base"))
        self.assertTrue(check_license("activity"))

    def test_unknown_feature_fails_even_in_dev_mode(self):
        self.assertFalse(check_license("vip"))  # type: ignore[arg-type]

    def test_typo_in_skip_flag_still_passes(self):
        os.environ["MAATTA_DEV_SKIP_CDK"] = "enable"
        self.assertTrue(check_license("base"))


class Phase1LayoutTests(unittest.TestCase):
    def test_interface_entries_and_agent_path(self):
        text = (ROOT / "assets" / "interface.json").read_text(encoding="utf-8")
        self.assertIn('"name": "MaaTTA"', text)
        self.assertIn("https://github.com/gityangchen/MaaTTA", text)
        self.assertIn('"display_short_side": 720', text)
        self.assertIn('"../agent/main.py"', text)
        self.assertNotIn("MyTask", text)
        self.assertNotIn("MaaXXX", text)
        entries = re.findall(r'"entry"\s*:\s*"([^"]+)"', text)
        nodes = _pipeline_nodes()
        self.assertEqual(
            entries,
            ["Phase1AwardMail", "HomeAnchorProbe", "CdkCheckDev"],
        )
        for entry in entries:
            self.assertIn(entry, nodes)

    def test_pipeline_refs_resolve_and_demo_is_gone(self):
        nodes = _pipeline_nodes()
        self.assertNotIn("MyTask1", nodes)
        self.assertNotIn("FindSmallestNumber", nodes)
        self.assertNotIn("click_target", json.dumps(nodes, ensure_ascii=False))
        for name, node in nodes.items():
            for key in ("next", "on_error"):
                for ref in _refs(node.get(key, [])):
                    self.assertIn(ref, nodes, f"{name}.{key} -> {ref}")
        self.assertIn("cdk_gate", json.dumps(nodes, ensure_ascii=False))
        self.assertIn("check_cdk", json.dumps(nodes, ensure_ascii=False))

    def test_checklist_lists_every_template(self):
        nodes = _pipeline_nodes()
        checklist = (ROOT / "docs" / "zh_cn" / "phase1_checklist.md").read_text(
            encoding="utf-8"
        )
        templates = []
        for node in nodes.values():
            templates.extend(_templates(node))
        self.assertGreaterEqual(len(templates), 20)
        missing = [item for item in templates if item not in checklist]
        self.assertEqual(missing, [])
        for item in templates:
            self.assertTrue(item.startswith("phase1/"))
            self.assertTrue(item.endswith(".png"))

    def test_missing_images_are_ignored_until_crops_land(self):
        config = (ROOT / "maatools.config.mts").read_text(encoding="utf-8")
        self.assertIn("'unknown-image': 'ignore'", config)
        checklist = (ROOT / "docs" / "zh_cn" / "phase1_checklist.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("unknown-image", checklist)

    def test_phase1_pngs_are_captured_crops_only(self):
        image_dir = ROOT / "assets" / "resource" / "image" / "phase1"
        pngs = sorted(
            path.relative_to(image_dir).as_posix()
            for path in image_dir.rglob("*.png")
        )
        self.assertEqual(
            pngs,
            [
                "friends/back.png",
                "friends/entry.png",
                "home/anchor.png",
                "mail/back.png",
                "mail/entry.png",
                "popup/generic_close.png",
            ],
        )
        for rel in pngs:
            data = (image_dir / rel).read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"), rel)
            self.assertGreater(len(data), 64, rel)

    def test_later_phases_have_comments_only(self):
        pipeline = ROOT / "assets" / "resource" / "pipeline"
        for phase in ("phase2", "phase3", "phase4"):
            directory = pipeline / phase
            self.assertEqual(list(directory.glob("*.json")), [])
            readme = (directory / "README.md").read_text(encoding="utf-8")
            self.assertIn("pipeline", readme.lower())
        phase4 = (pipeline / "phase4" / "README.md").read_text(encoding="utf-8")
        self.assertIn("搜 UID", phase4)
        self.assertIn("拜访家园", phase4)
        self.assertIn("份数上限", phase4)
        self.assertIn("activity", phase4)

    def test_mail_path_is_home_friends_mail_then_dispatch(self):
        nodes = _pipeline_nodes()
        home_next = nodes["HomeGate"]["next"]
        self.assertEqual(
            home_next,
            [
                "FriendsEntry",
                "SignInEntry",
                "SevenDayEntry",
                "ActivityAwardEntry",
                "MarbleAwardEntry",
            ],
        )
        self.assertNotIn("MailEntry", home_next)

        dispatch_next = list(_refs(nodes["Phase1Dispatch"]["next"]))
        self.assertIn("HomeGate", dispatch_next)
        self.assertNotIn("MailEntry", dispatch_next)
        self.assertNotIn("FriendsEntry", dispatch_next)

        friends = nodes["FriendsEntry"]
        self.assertEqual(friends["recognition"], "TemplateMatch")
        self.assertEqual(friends["action"], "Click")
        self.assertEqual(friends["template"], "phase1/friends/entry.png")
        self.assertEqual(friends["max_hit"], 1)
        self.assertEqual(friends["next"], ["FriendsBoard"])

        board_next = nodes["FriendsBoard"]["next"]
        by_name = {}
        for item in board_next:
            if isinstance(item, str):
                by_name[item] = None
            else:
                by_name[item["name"]] = item
        for popup in (
            "PopupMaintenance",
            "PopupUpdateLater",
            "PopupNetworkConfirm",
            "PopupGenericClose",
            "PopupBlockingOcr",
        ):
            self.assertIn(popup, by_name)
            self.assertTrue(by_name[popup]["jump_back"])
        self.assertEqual(by_name["MailEntry"], None)
        self.assertEqual(nodes["FriendsBoard"]["recognition"], "DirectHit")
        self.assertEqual(nodes["FriendsBoard"]["action"], "DoNothing")

        mail = nodes["MailEntry"]
        self.assertEqual(mail["template"], "phase1/mail/entry.png")
        self.assertEqual(mail["action"], "Click")
        self.assertEqual(mail["next"], ["MailBoard"])
        mail_board_next = list(_refs(nodes["MailBoard"]["next"]))
        self.assertIn("MailEmpty", mail_board_next)
        self.assertIn("MailEmptyOcr", mail_board_next)
        self.assertIn("MailBack", mail_board_next)
        self.assertIn("PopupNetworkConfirm", mail_board_next)
        self.assertEqual(nodes["MailBack"]["next"], ["FriendsBack"])
        self.assertEqual(nodes["MailBack"]["template"], "phase1/mail/back.png")

        friends_back = nodes["FriendsBack"]
        self.assertEqual(friends_back["recognition"], "TemplateMatch")
        self.assertEqual(friends_back["action"], "Click")
        self.assertEqual(friends_back["template"], "phase1/friends/back.png")
        self.assertEqual(friends_back["next"], ["Phase1Dispatch"])

        templates = []
        for node in nodes.values():
            templates.extend(_templates(node))
        self.assertIn("phase1/friends/entry.png", templates)
        self.assertIn("phase1/friends/back.png", templates)
        friends_entry = (
            ROOT / "assets" / "resource" / "image" / "phase1" / "friends" / "entry.png"
        )
        self.assertTrue(friends_entry.is_file())
        self.assertTrue(friends_entry.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
        friends_back_png = (
            ROOT / "assets" / "resource" / "image" / "phase1" / "friends" / "back.png"
        )
        self.assertTrue(friends_back_png.is_file())
        self.assertTrue(friends_back_png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))

        checklist = (ROOT / "docs" / "zh_cn" / "phase1_checklist.md").read_text(
            encoding="utf-8"
        )
        report = (ROOT / "docs" / "zh_cn" / "phase1_crop_report.md").read_text(
            encoding="utf-8"
        )
        for text in (checklist, report):
            self.assertIn("主界面 → 好友 → 邮件", text)
            self.assertIn("phase1/friends/entry.png", text)
            self.assertIn("720×1280", text)
            self.assertIn("FriendsBack", text)
        self.assertIn("phase1/friends/entry.png", checklist)
        self.assertIn("phase1/friends/back.png", checklist)
        self.assertIn("`FriendsBack`", checklist)
        self.assertNotIn("不要造 `phase1/friends/back.png`", checklist)

    def test_packaged_agent_path_rewrite(self):
        install = _load_install()
        self.assertEqual(
            install.packaged_agent_args(["../agent/main.py"]),
            ["./agent/main.py"],
        )
        self.assertEqual(
            install.packaged_agent_args(["--flag", "../agent/main.py"]),
            ["--flag", "./agent/main.py"],
        )


if __name__ == "__main__":
    unittest.main()

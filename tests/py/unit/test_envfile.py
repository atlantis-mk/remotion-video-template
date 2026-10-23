"""L1 单元：lib/envfile.py（.env 解析、Key 校验、Secret）与 lib/log.py（Redactor）（F-17、NF-02）；签名按架构 v1.2 §7.5"""
from py.support import SkillTestCase, covers, FAKE_KEY

class TestEnvfile(SkillTestCase):
    @covers("U-ENV-01", "F-17")
    def test_parse_env_basic(self):
        """解析 KEY=VALUE、忽略注释和空行、去引号"""
        parse_env = self.attr(self.lib("envfile"), "parse_env")
        txt = '# c\n\nDOUBAO_TTS_API_KEY="abc"\nDOUBAO_SPEAKER=\'spk\'\n  # x\n'
        self.assertEqual(parse_env(txt), {"DOUBAO_TTS_API_KEY": "abc", "DOUBAO_SPEAKER": "spk"})

    @covers("U-ENV-02", "F-17")
    def test_load_env_missing_file(self):
        """.env 不存在 → MissingKeyError，消息含 .env 绝对路径与变量名"""
        m = self.lib("envfile"); err = self.attr(m, "MissingKeyError")
        d = self.tmpdir()
        with self.assertRaises(err) as cm:
            m.load_env(d)
        self.assertIn(str((d / ".env").resolve()), str(cm.exception))
        self.assertIn("DOUBAO_TTS_API_KEY", str(cm.exception))

    @covers("U-ENV-03", "F-17")
    def test_load_env_empty_or_blank_key(self):
        """Key 为空或空白 → MissingKeyError"""
        m = self.lib("envfile"); err = self.attr(m, "MissingKeyError")
        for body in ("DOUBAO_TTS_API_KEY=\n", "DOUBAO_TTS_API_KEY=   \n", "# only comment\n"):
            d = self.tmpdir(); (d / ".env").write_text(body)
            with self.assertRaises(err):
                m.load_env(d)

    @covers("U-ENV-04", "F-17")
    def test_load_env_ignores_process_env(self):
        """只从 .env 读取：进程环境变量有 Key 但 .env 缺失时仍报缺失"""
        import os
        m = self.lib("envfile"); err = self.attr(m, "MissingKeyError")
        d = self.tmpdir(); os.environ["DOUBAO_TTS_API_KEY"] = FAKE_KEY
        try:
            with self.assertRaises(err):
                m.load_env(d)
        finally:
            os.environ.pop("DOUBAO_TTS_API_KEY", None)

    @covers("U-ENV-05", "F-17", "NF-02")
    def test_load_env_valid_secret_masked(self):
        """有效 Key：Secret 的 repr/str 为 ***，reveal() 返回原值，不写入 os.environ"""
        import os
        m = self.lib("envfile")
        d = self.tmpdir(); (d / ".env").write_text(f"DOUBAO_TTS_API_KEY={FAKE_KEY}\nDOUBAO_SPEAKER=spk1\n")
        cfg = m.load_env(d)
        key = cfg.key
        self.assertEqual(str(key), "***"); self.assertEqual(repr(key), "***")
        self.assertNotIn(FAKE_KEY, repr(cfg)); self.assertNotIn(FAKE_KEY, str(cfg))
        self.assertEqual(key.reveal(), FAKE_KEY)
        self.assertEqual(cfg.speaker, "spk1")
        self.assertNotEqual(os.environ.get("DOUBAO_TTS_API_KEY"), FAKE_KEY)

    @covers("U-ENV-06", "NF-02", "F-05")
    def test_redactor(self):
        """Redactor 把 Key 原文替换为 ***"""
        R = self.libfn("log", "Redactor")  # §7.5：Redactor 在 lib/log.py
        r = R(secrets=[FAKE_KEY])
        out = r.redact(f"auth failed key={FAKE_KEY} again {FAKE_KEY}")
        self.assertNotIn(FAKE_KEY, out); self.assertEqual(out.count("***"), 2)

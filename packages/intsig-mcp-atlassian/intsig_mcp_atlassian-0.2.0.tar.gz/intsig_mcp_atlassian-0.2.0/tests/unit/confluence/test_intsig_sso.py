import os

import pytest

from intsig_mcp_atlassian.confluence.config import ConfluenceConfig
from intsig_mcp_atlassian.utils.intsig_sso import encrypt_password


def test_encrypt_password_roundtrip_like_properties():
    # 只是校验输出为偶数长度的hex字符串
    plaintext = "34504?Ghy"
    encrypted = encrypt_password(plaintext)
    assert isinstance(encrypted, str)
    assert len(encrypted) % 2 == 0
    int(encrypted, 16)  # 不应抛出


def test_config_detects_intsig_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("INTSIG_CONFLUENCE_URL", "https://doc.intsig.net")
    monkeypatch.setenv("INTSIG_CONFLUENCE_EMAIL", "user@example.com")
    monkeypatch.setenv("INTSIG_CONFLUENCE_PWD", "secretpwd")

    # 确保标准变量缺失时仍能被 INTSIG_* 驱动
    monkeypatch.delenv("CONFLUENCE_URL", raising=False)
    monkeypatch.delenv("CONFLUENCE_USERNAME", raising=False)
    monkeypatch.delenv("CONFLUENCE_API_TOKEN", raising=False)

    cfg = ConfluenceConfig.from_env()
    assert cfg.auth_type == "intsig_sso"
    assert cfg.url == "https://doc.intsig.net"
    assert cfg.username == "user@example.com"
    # 在 INTSIG 模式下，api_token 字段承载“真实密码”用于 Basic 头
    assert cfg.api_token == "secretpwd"







import os
import pytest

from intsig_mcp_atlassian.confluence.client import ConfluenceClient


def _intsig_env_ready() -> tuple[bool, list[str]]:
    required = [
        "INTSIG_CONFLUENCE_URL",
        "INTSIG_CONFLUENCE_EMAIL",
        "INTSIG_CONFLUENCE_PWD",
    ]
    missing = [name for name in required if not os.getenv(name)]
    return (len(missing) == 0, missing)


@pytest.mark.integration
def test_confluence_intsig_sso_smoke():
    ready, missing = _intsig_env_ready()
    if not ready:
        pytest.skip(
            f"INTSIG_* env vars not set; missing: {', '.join(missing)}"
        )

    client = ConfluenceClient()  # 自动选择 intsig_sso

    # 触发一次简单 API 调用：获取空间列表首页
    spaces = client.confluence.get_all_spaces(limit=5)
    assert spaces is not None
    assert isinstance(spaces, dict)
    # 结果结构通常包含 'results' 列表
    assert "results" in spaces
    assert isinstance(spaces["results"], list)



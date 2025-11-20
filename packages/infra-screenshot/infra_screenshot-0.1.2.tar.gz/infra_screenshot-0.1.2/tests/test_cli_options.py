import pytest

from screenshot._shared.cli.options import build_options
from screenshot._shared.cli.schema import ScreenshotCliArgs


def _make_args() -> ScreenshotCliArgs:
    return ScreenshotCliArgs(
        input=None,
        urls=("https://example.com",),
        site_ids=("demo",),
        partition_date=None,
        max_pages=1,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=1.0,
        timeout_s=30.0,
        max_retries=1,
        job_budget_s=None,
        scroll=None,
        allow_autoplay=None,
        hide_overlays=None,
        reduced_motion=None,
        full_page=None,
        pre_capture_wait_s=None,
        mute_media=None,
        disable_animations=None,
        block_media=None,
        extra_css_paths=(),
        extra_js_paths=(),
        chromium_compat=None,
        max_viewport_concurrency=None,
        override_custom_user_agent=None,
        playwright_executable_path=None,
        backend="playwright",
    )


def test_build_options_rejects_flat_payload() -> None:
    args = _make_args()
    with pytest.raises(ValueError, match="nested 'capture'"):
        build_options(
            args=args,
            css_snippets=(),
            js_snippets=(),
            overrides={"max_pages": 5},
        )


def test_build_options_accepts_nested_payload() -> None:
    args = _make_args()
    options = build_options(
        args=args,
        css_snippets=(),
        js_snippets=(),
        overrides={
            "schema_version": "screenshot_options/v2",
            "capture": {"enabled": True, "max_pages": 3},
        },
    )

    assert options.capture.enabled is True
    assert options.capture.max_pages == 3

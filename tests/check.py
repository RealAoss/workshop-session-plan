from pathlib import Path

import os
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]

with sync_playwright() as p, TemporaryDirectory() as temp:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH"))
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto((ROOT / "index.html").as_uri())
    page.locator("#f0").fill("Updated session details")
    assert "Updated session details" in page.locator("#result").inner_text()
    with page.expect_download() as exported:
        page.locator("#save").click()
    dest = Path(temp) / "result.txt"
    exported.value.save_as(dest)
    assert dest.read_text(encoding="utf-8") == page.locator("#result").inner_text()
    page.locator("#f0").fill("")
    assert "Updated session details" not in page.locator("#result").inner_text()
    assert not errors, errors
    browser.close()

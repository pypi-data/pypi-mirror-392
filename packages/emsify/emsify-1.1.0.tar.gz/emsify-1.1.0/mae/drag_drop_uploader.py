#!/usr/bin/env python3
"""
DragDropUploader - Robust file upload for EMS portals
Supports 4 strategies: direct input, hidden input, JS drag-drop, click dialog
"""
import base64, json, time
from pathlib import Path
from typing import List, Sequence, Tuple, Union
from selenium.common.exceptions import ElementNotInteractableException, JavascriptException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class DragDropUploader:
    def __init__(self, driver):
        self.dr = driver

    def drag_file_to_dropzone(self, file_paths: Union[str, Sequence[str]], dropzone_selector: str,
                               timeout: int = 10, retry: bool = True, verbose: bool = False) -> Tuple[bool, str]:
        paths = self._normalize_paths(file_paths)
        missing = [str(p) for p in paths if not p.is_file()]
        if missing:
            if verbose: print(f"[drag_file] Missing: {', '.join(missing)}")
            return False, "file_not_found"

        try:
            dropzone = self._wait_for_element(dropzone_selector, timeout)
        except TimeoutException:
            if verbose: print(f"[drag_file] Dropzone not found: {dropzone_selector}")
            return False, "dropzone_not_found"

        strategies = (
            ("direct_input", self._strategy_direct_input),
            ("hidden_input", self._strategy_hidden_input),
            ("js_drag", self._strategy_js_drag),
            ("click_dialog", self._strategy_click_dialog),
        )

        for name, func in strategies:
            try:
                if func(dropzone, paths, verbose=verbose):
                    return True, name
            except Exception as exc:
                if verbose: print(f"[{name}] {type(exc).__name__}: {exc}")
            if not retry: break

        if verbose: print("[drag_file] All strategies failed")
        return False, "all_failed"

    def _strategy_direct_input(self, dropzone: WebElement, paths: List[Path], *, verbose: bool = False) -> bool:
        if dropzone.tag_name.lower() == "input" and "file" in (dropzone.get_attribute("type") or ""):
            try:
                dropzone.send_keys("\n".join(str(p) for p in paths))
                if verbose: print("[direct_input] Success")
                return True
            except ElementNotInteractableException as exc:
                if verbose: print(f"[direct_input] Not interactable: {exc}")
        return False

    def _strategy_hidden_input(self, dropzone: WebElement, paths: List[Path], *, verbose: bool = False) -> bool:
        inputs = dropzone.find_elements(By.XPATH, ".//input[@type='file']")
        if not inputs:
            inputs = self.dr.find_elements(By.CSS_SELECTOR, "input[type='file']")

        for inp in inputs:
            try:
                self._unhide_element(inp)
                inp.send_keys("\n".join(str(p) for p in paths))
                self._rehide_element(inp)
                if verbose: print("[hidden_input] Success")
                return True
            except Exception as exc:
                if verbose: print(f"[hidden_input] Failed: {exc}")
        return False

    def _strategy_js_drag(self, dropzone: WebElement, paths: List[Path], *, verbose: bool = False) -> bool:
        files_json = json.dumps([self._file_to_js_dict(p) for p in paths])
        js = """
const target = arguments[0], filesData = JSON.parse(arguments[1]);
const dataTransfer = (typeof DataTransfer !== 'undefined') ? new DataTransfer() : (new ClipboardEvent('').clipboardData || new DataTransfer());
for (const f of filesData) {
    const bin = Uint8Array.from(atob(f.content), c => c.charCodeAt(0));
    const file = new File([bin], f.name, {type: f.type});
    dataTransfer.items.add(file);
}
for (const evtName of ['dragenter', 'dragover', 'drop']) {
    const evt = new DragEvent(evtName, {bubbles: true, cancelable: true, dataTransfer: dataTransfer});
    target.dispatchEvent(evt);
}
let inputResult = false;
target.querySelectorAll('input[type=file]').forEach(inp => {
    try {
        Object.defineProperty(inp, 'files', {value: dataTransfer.files});
        const changeEvt = new Event('change', {bubbles: true});
        inp.dispatchEvent(changeEvt);
        inputResult = true;
    } catch(e) {}
});
return {dropResult: true, inputResult: inputResult};
"""
        try:
            res = self.dr.execute_script(js, dropzone, files_json)
        except JavascriptException as exc:
            if verbose: print(f"[js_drag] JS error: {exc}")
            return False

        if (res or {}).get("dropResult") or (res or {}).get("inputResult"):
            if verbose: print("[js_drag] Success")
            return True
        if verbose: print(f"[js_drag] Returned {res}")
        return False

    def _strategy_click_dialog(self, dropzone: WebElement, paths: List[Path], *, verbose: bool = False) -> bool:
        try:
            self.dr.execute_script("arguments[0].scrollIntoView({block:'center'});", dropzone)
            time.sleep(0.4)
            try:
                dropzone.click()
            except:
                self.dr.execute_script("arguments[0].click();", dropzone)
            if verbose: print("[click_dialog] Dialog opened – manual selection needed")
        except Exception as exc:
            if verbose: print(f"[click_dialog] Could not click: {exc}")
        return False

    def _wait_for_element(self, selector: str, timeout: int) -> WebElement:
        by = By.XPATH if selector.lstrip().startswith("//") else By.CSS_SELECTOR
        return WebDriverWait(self.dr, timeout).until(EC.presence_of_element_located((by, selector)))

    @staticmethod
    def _normalize_paths(file_paths: Union[str, Sequence[str]]) -> List[Path]:
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]
        return [Path(p).expanduser().resolve() for p in file_paths]

    def _unhide_element(self, el: WebElement):
        self.dr.execute_script("""
const e = arguments[0];
e.dataset._oldDisplay = e.style.display;
e.dataset._oldVisibility = e.style.visibility;
e.style.display = 'block';
e.style.visibility = 'visible';
""", el)

    def _rehide_element(self, el: WebElement):
        self.dr.execute_script("""
const e = arguments[0];
e.style.display = e.dataset._oldDisplay;
e.style.visibility = e.dataset._oldVisibility;
""", el)

    @staticmethod
    def _file_to_js_dict(path: Path) -> dict:
        with path.open("rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        return {"name": path.name, "size": path.stat().st_size, "type": DragDropUploader._get_mime_type(path), "content": b64}

    @staticmethod
    def _get_mime_type(path: Path) -> str:
        ext = path.suffix.lower()
        return {
            ".txt": "text/plain", ".pdf": "application/pdf", ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
            ".csv": "text/csv", ".zip": "application/zip", ".mp3": "audio/mpeg", ".mp4": "video/mp4",
            ".json": "application/json", ".xml": "application/xml"
        }.get(ext, "application/octet-stream")

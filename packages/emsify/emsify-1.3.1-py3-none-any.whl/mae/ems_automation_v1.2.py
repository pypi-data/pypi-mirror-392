"""
EMS Automation v1.2.0 - Refactored to inherit from TrackedEmsWalk
Eliminates duplicate frame logic, adds security fixes
"""
import time, atexit
from pathlib import Path
from typing import Optional, Dict, List
from collections import defaultdict
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from .ems_walk import TrackedEmsWalk

class EmsAutomation(TrackedEmsWalk):
    """Unified automation for complex EMS portals with nested frames"""
    
    def __init__(self, driver, max_depth: int = 10, log_path: Optional[Path] = None, 
                 verbose: bool = True, validate_path: bool = True):
        super().__init__(driver, max_depth=max_depth, verbose=verbose)
        self.validate_path = validate_path
        self._logs: List[Dict] = []
        self._error_counts = defaultdict(int)
        self.log_path = log_path or self._auto_log_path()
        try:
            from .drag_drop_uploader import DragDropUploader
            self.uploader = DragDropUploader(self.dr)
        except ImportError:
            self.uploader = None
        atexit.register(self._flush_logs)
        if verbose: print(f'[EMS] Connected: {self.dr.title}')
    
    def _auto_log_path(self) -> Path:
        try:
            domain = urlparse(self.dr.current_url).netloc.split(':')[0].replace('.', '_')
            return Path(f'{domain}_log.csv')
        except: return Path('ems_log.csv')
    
    def _handle_error(self, err: Exception, context: str = ''):
        """Track errors for statistics"""
        err_name = type(err).__name__
        self._error_counts[err_name] += 1
        if self._verbose: print(f'[ERR] {err_name}: {context}')
    
    def _validate_file_path(self, path: str) -> Path:
        """Validate file path to prevent traversal attacks"""
        if not self.validate_path:
            return Path(path)
        p = Path(path).resolve()
        cwd = Path.cwd().resolve()
        try:
            p.relative_to(cwd)
            return p
        except ValueError:
            raise ValueError(f"Path outside allowed directory: {p}")
    
    def locate(self, sel: str, timeout: int = 5, method: str = 'selenium', 
               condition: str = 'visible', check_visible: bool = True, 
               default_first: bool = True) -> Optional[WebElement]:
        """Locate element using smart frame search from TrackedEmsWalk"""
        if not sel or not isinstance(sel, str):
            raise ValueError(f"Invalid selector: {sel}")
        if timeout <= 0:
            raise ValueError(f"Timeout must be positive: {timeout}")
        
        start = time.time()
        if method == 'js':
            elem = self.locate_element_js(sel, t=timeout, default_first=default_first, 
                                         check_visibility=check_visible)
        else:
            func = f'wait_for_{condition}'
            elem = self.locate_element(sel, t=timeout, func=func, default_first=default_first)
        
        duration = time.time() - start
        if elem:
            self._log_success(sel, method, duration)
        else:
            self._log_failure(sel, method, duration)
        return elem
    
    def click(self, sel: str, timeout: int = 5, force_js: bool = False) -> bool:
        elem = self.locate(sel, timeout)
        if not elem: return False
        strategies = [
            lambda: elem.click(),
            lambda: self.dr.execute_script('arguments[0].click()', elem),
            lambda: ActionChains(self.dr).move_to_element(elem).click().perform()
        ]
        if force_js: strategies = strategies[1:]
        for strategy in strategies:
            try:
                strategy()
                return True
            except Exception as e:
                self._handle_error(e, f'click: {sel}')
        return False
    
    def send_keys(self, sel: str, text: str, timeout: int = 5, clear: bool = True) -> bool:
        elem = self.locate(sel, timeout)
        if not elem: return False
        try:
            if clear: elem.clear()
            elem.send_keys(text)
            return True
        except Exception as e:
            self._handle_error(e, f'send_keys: {sel}')
            return False
    
    def hover_click(self, hover_sel: str, click_sel: str, timeout: int = 5) -> bool:
        hover_elem = self.locate(hover_sel, timeout)
        if not hover_elem: return False
        try:
            ActionChains(self.dr).move_to_element(hover_elem).perform()
            time.sleep(0.5)
            return self.click(click_sel, timeout)
        except Exception as e:
            self._handle_error(e, f'hover_click: {hover_sel} -> {click_sel}')
            return False
    
    def upload_file(self, file_path: str, dropzone_sel: str, timeout: int = 10) -> bool:
        path = self._validate_file_path(file_path)
        if not path.is_file():
            if self._verbose: print(f'[UPLOAD] File not found: {file_path}')
            return False
        if self.uploader:
            if self._verbose: print(f'[UPLOAD] Using DragDropUploader for: {file_path}')
            success, strategy = self.uploader.drag_file_to_dropzone(
                file_paths=str(path), dropzone_selector=dropzone_sel,
                timeout=timeout, verbose=self._verbose)
            return success
        dropzone = self.locate(dropzone_sel, timeout)
        if not dropzone: return False
        if dropzone.tag_name == 'input' and dropzone.get_attribute('type') == 'file':
            try:
                dropzone.send_keys(str(path))
                return True
            except Exception as e:
                self._handle_error(e, 'upload_direct')
        for inp in self.dr.find_elements(By.CSS_SELECTOR, 'input[type=file]'):
            try:
                self.dr.execute_script("arguments[0].style.display='block';arguments[0].style.visibility='visible'", inp)
                inp.send_keys(str(path))
                return True
            except Exception as e:
                self._handle_error(e, 'upload_hidden')
        if self._verbose: print(f'[UPLOAD] All strategies failed')
        return False
    
    def scroll(self, direction: str = 'down', pixels: int = 500):
        x, y = (pixels, 0) if direction == 'right' else (0, pixels)
        if direction in ('up', 'left'): x, y = -x, -y
        self.dr.execute_script(f'window.scrollBy({x},{y})')
    
    def scroll_to_bottom(self, step: int = 800, pause: float = 0.2):
        last_h = 0
        while True:
            h = self.dr.execute_script('return document.body.scrollHeight')
            if h == last_h: break
            last_h = h
            for y in range(0, h, step):
                self.dr.execute_script(f'window.scrollTo(0,{y})')
                time.sleep(pause)
    
    def handle_alert(self, action: str = 'accept', timeout: int = 3) -> bool:
        try:
            alert = WebDriverWait(self.dr, timeout).until(EC.alert_is_present())
            if action == 'accept': alert.accept()
            else: alert.dismiss()
            return True
        except TimeoutException:
            return False
    
    def switch_to_new_window(self):
        windows = self.dr.window_handles
        if len(windows) > 1:
            self.dr.switch_to.window(windows[-1])
            if self._verbose: print(f'[WINDOW] Switched to: {self.dr.title}')
    
    def _log_success(self, sel: str, method: str, duration: float):
        self._logs.append({'selector': sel, 'method': method, 'status': 'ok',
                          'duration': round(duration, 3), 'frame': self.ctx_path,
                          'url': self.dr.current_url, 'time': time.time()})
        if len(self._logs) >= 500:
            self._flush_logs()
    
    def _log_failure(self, sel: str, method: str, duration: float):
        self._logs.append({'selector': sel, 'method': method, 'status': 'fail',
                          'duration': round(duration, 3), 'frame': self.ctx_path,
                          'url': self.dr.current_url, 'time': time.time()})
        if len(self._logs) >= 500:
            self._flush_logs()
    
    def _flush_logs(self):
        if not self._logs: return
        import csv
        exists = self.log_path.exists()
        with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['selector','method','status','duration','frame','url','time'])
            if not exists: writer.writeheader()
            writer.writerows(self._logs)
        if self._verbose: print(f'[LOG] Saved {len(self._logs)} entries to {self.log_path}')
        self._logs.clear()
    
    def save_logs(self):
        self._flush_logs()
    
    def get_stats(self) -> Dict:
        return dict(self._error_counts)
    
    @property
    def frame_path(self) -> str:
        """Backward compatibility alias for ctx_path"""
        return self.ctx_path

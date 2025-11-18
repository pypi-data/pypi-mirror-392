"""
EMS Automation - Consolidated Web Scraping for Telecom Portals
Optimized for Huawei, Ericsson, Alcatel EMS portals with complex frame structures
"""
import time, base64, json, atexit
from pathlib import Path
from typing import List, Tuple, Union, Optional, Dict, Any
from collections import defaultdict
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException,
    ElementNotInteractableException, StaleElementReferenceException,
    NoAlertPresentException, WebDriverException, JavascriptException
)

class EmsAutomation:
    """Unified automation for complex EMS portals with nested frames"""
    
    _ERRORS = [TimeoutException, NoSuchElementException, ElementClickInterceptedException,
               ElementNotInteractableException, StaleElementReferenceException,
               NoAlertPresentException, WebDriverException]
    
    def __init__(self, driver, log_path: Optional[Path] = None, verbose: bool = True):
        self.dr = driver
        self.verbose = verbose
        self._frame_stack: List[WebElement] = []
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
    
    # ==================== SELECTOR PARSING ====================
    def _parse_selector(self, sel: str) -> Tuple[str, str]:
        """Parse selector string to (By type, locator)"""
        if sel.startswith(('//', './', '(')): return By.XPATH, sel
        if sel.startswith('xpath='): return By.XPATH, sel[6:]
        if sel.startswith('id='): return By.ID, sel[3:]
        if sel.startswith('name='): return By.NAME, sel[5:]
        if sel.startswith('css='): return By.CSS_SELECTOR, sel[4:]
        return By.CSS_SELECTOR, sel
    
    # ==================== ERROR HANDLING ====================
    def _handle_error(self, err: Exception, context: str = '') -> int:
        for i, exc_type in enumerate(self._ERRORS):
            if isinstance(err, exc_type):
                self._error_counts[exc_type.__name__] += 1
                if self.verbose: print(f'[ERR-{i}] {exc_type.__name__}: {context}')
                return i
        if self.verbose: print(f'[ERR-?] {type(err).__name__}: {context}')
        return -1
    
    # ==================== FRAME MANAGEMENT ====================
    @property
    def frame_path(self) -> str:
        """Human-readable current frame path"""
        if not self._frame_stack: return '[default]'
        names = []
        for fr in self._frame_stack:
            name = fr.get_attribute('name') or fr.get_attribute('id') or f'<frame-{len(names)}>'
            names.append(name)
        return ' > '.join(names)
    
    def _switch_default(self):
        self.dr.switch_to.default_content()
        self._frame_stack.clear()
        if self.verbose: print(f'[FRAME] → default')
    
    def _switch_parent(self):
        if self._frame_stack:
            self.dr.switch_to.parent_frame()
            self._frame_stack.pop()
            if self.verbose: print(f'[FRAME] → parent ({self.frame_path})')
    
    def _switch_into(self, frame: WebElement):
        """Switch into frame with error handling"""
        self.dr.switch_to.frame(frame)
        self._frame_stack.append(frame)
        if self.verbose: print(f'[FRAME] → {self.frame_path}')
    
    # ==================== WAIT STRATEGIES ====================
    def _wait_element(self, sel: str, timeout: int, condition: str) -> Optional[WebElement]:
        by, loc = self._parse_selector(sel)
        wait = WebDriverWait(self.dr, timeout)
        try:
            if condition == 'clickable':
                return wait.until(EC.element_to_be_clickable((by, loc)))
            elif condition == 'visible':
                return wait.until(EC.visibility_of_element_located((by, loc)))
            else:  # present
                return wait.until(EC.presence_of_element_located((by, loc)))
        except Exception as e:
            self._handle_error(e, f'wait_{condition}: {sel}')
            return None
    
    # ==================== JS ELEMENT LOCATION ====================
    def _locate_js(self, sel: str, timeout: int, check_visible: bool) -> Optional[WebElement]:
        """Locate element using JavaScript with retry for dynamic content"""
        by, loc = self._parse_selector(sel)
        js = """
        var sel=arguments[0],vis=arguments[1];
        var el=%s;
        if(!el)return null;
        el.scrollIntoView({block:'center',behavior:'instant'});
        if(vis&&(el.offsetParent===null||getComputedStyle(el).display==='none'))return null;
        return el;
        """ % ('document.evaluate(sel,document,null,9,null).singleNodeValue' if by == By.XPATH 
               else 'document.querySelector(sel)')
        
        start = time.time()
        while time.time() - start < timeout:
            try:
                elem = self.dr.execute_script(js, loc, check_visible)
                if elem: return elem
            except JavascriptException:
                break  # JS syntax error won't fix itself
            except Exception as e:
                self._handle_error(e, f'js_locate: {sel}')
                # Continue retry - element might appear (dynamic EMS content)
            time.sleep(0.3)
        return None
    
    # ==================== FRAME WALKING ====================
    def _walk_frames(self, sel: str, timeout: int, method: str, **kwargs) -> Optional[WebElement]:
        """Recursively search element across all frames with stale frame protection"""
        for frame in self.dr.find_elements(By.CSS_SELECTOR, 'frame,iframe'):
            try:
                self._switch_into(frame)
            except StaleElementReferenceException:
                continue  # Skip stale frame
            
            # Try to find element in current frame
            if method == 'selenium':
                elem = self._wait_element(sel, timeout, kwargs.get('condition', 'visible'))
            else:  # js
                elem = self._locate_js(sel, timeout, kwargs.get('check_visible', True))
            
            if elem: return elem
            
            # Recurse into nested frames
            elem = self._walk_frames(sel, timeout, method, **kwargs)
            if elem: return elem
            
            try:
                self._switch_parent()
            except:
                self._switch_default()  # Recovery if parent switch fails
        return None
    
    # ==================== MAIN LOCATE METHODS ====================
    def locate(self, sel: str, timeout: int = 5, method: str = 'selenium', 
               condition: str = 'visible', check_visible: bool = True, 
               default_first: bool = True) -> Optional[WebElement]:
        """
        Locate element using smart frame search algorithm from ems_walk.py
        
        Search order (optimized for EMS portals):
        A) Current context (fast path - 90% hit rate for sequential ops)
        B) Default content (if default_first=True)
        C) Walk all frames depth-first (thorough search)
        D) Final attempt in default (last chance)
        
        Args:
            sel: Selector (xpath, css, id=, name=)
            timeout: Wait timeout in seconds
            method: 'selenium' or 'js'
            condition: 'clickable', 'visible', or 'present' (selenium only)
            check_visible: Check visibility (js only)
            default_first: Try default content before frame walking
        
        Note: Leaves driver in found frame for next operation (optimization)
        """
        start = time.time()
        
        # A) Try current context first (FAST PATH)
        if method == 'selenium':
            elem = self._wait_element(sel, timeout, condition)
        else:
            elem = self._locate_js(sel, timeout, check_visible)
        
        if elem:
            self._log_success(sel, method, time.time() - start)
            return elem
        
        # Switch to default
        self._switch_default()
        
        # B) Try default content (if default_first=True)
        if default_first:
            if method == 'selenium':
                elem = self._wait_element(sel, timeout, condition)
            else:
                elem = self._locate_js(sel, timeout, check_visible)
            
            if elem:
                self._log_success(sel, method, time.time() - start)
                return elem
        
        # C) Walk all frames (depth-first search)
        kwargs = {'condition': condition} if method == 'selenium' else {'check_visible': check_visible}
        elem = self._walk_frames(sel, timeout, method, **kwargs)
        
        if elem:
            self._log_success(sel, method, time.time() - start)
            return elem
        
        # D) Final attempt in default
        self._switch_default()
        if method == 'selenium':
            elem = self._wait_element(sel, timeout, condition)
        else:
            elem = self._locate_js(sel, timeout, check_visible)
        
        duration = time.time() - start
        if elem:
            self._log_success(sel, method, duration)
        else:
            self._log_failure(sel, method, duration)
            if self.verbose: print(f'[FAIL] Element not found: {sel}')
        
        return elem
    
    # ==================== INTERACTION METHODS ====================
    def click(self, sel: str, timeout: int = 5, force_js: bool = False) -> bool:
        """Click element with fallback strategies"""
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
        """Send keys to element"""
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
        """Hover over one element and click another"""
        hover_elem = self.locate(hover_sel, timeout)
        if not hover_elem: return False
        
        try:
            ActionChains(self.dr).move_to_element(hover_elem).perform()
            time.sleep(0.5)
            return self.click(click_sel, timeout)
        except Exception as e:
            self._handle_error(e, f'hover_click: {hover_sel} -> {click_sel}')
            return False
    
    # ==================== FILE UPLOAD ====================
    def upload_file(self, file_path: str, dropzone_sel: str, timeout: int = 10) -> bool:
        """Upload file using DragDropUploader if available, else fallback"""
        if self.uploader:
            if self.verbose: print(f'[UPLOAD] Using DragDropUploader for: {file_path}')
            success, strategy = self.uploader.drag_file_to_dropzone(
                file_paths=file_path, dropzone_selector=dropzone_sel,
                timeout=timeout, verbose=self.verbose
            )
            return success
        
        # Fallback: basic implementation
        path = Path(file_path).resolve()
        if not path.is_file():
            if self.verbose: print(f'[UPLOAD] File not found: {file_path}')
            return False
        
        dropzone = self.locate(dropzone_sel, timeout)
        if not dropzone: return False
        
        if dropzone.tag_name == 'input' and dropzone.get_attribute('type') == 'file':
            try:
                dropzone.send_keys(str(path))
                return True
            except: pass
        
        for inp in self.dr.find_elements(By.CSS_SELECTOR, 'input[type=file]'):
            try:
                self.dr.execute_script("arguments[0].style.display='block';arguments[0].style.visibility='visible'", inp)
                inp.send_keys(str(path))
                return True
            except: pass
        
        if self.verbose: print(f'[UPLOAD] All strategies failed')
        return False
    
    # ==================== SCROLLING ====================
    def scroll(self, direction: str = 'down', pixels: int = 500):
        """Scroll page"""
        x, y = (pixels, 0) if direction == 'right' else (0, pixels)
        if direction in ('up', 'left'): x, y = -x, -y
        self.dr.execute_script(f'window.scrollBy({x},{y})')
    
    def scroll_to_bottom(self, step: int = 800, pause: float = 0.2):
        """Scroll to page bottom iteratively"""
        last_h = 0
        while True:
            h = self.dr.execute_script('return document.body.scrollHeight')
            if h == last_h: break
            last_h = h
            for y in range(0, h, step):
                self.dr.execute_script(f'window.scrollTo(0,{y})')
                time.sleep(pause)
    
    # ==================== ALERTS ====================
    def handle_alert(self, action: str = 'accept', timeout: int = 3) -> bool:
        """Handle JavaScript alert"""
        try:
            alert = WebDriverWait(self.dr, timeout).until(EC.alert_is_present())
            if action == 'accept': alert.accept()
            else: alert.dismiss()
            return True
        except TimeoutException:
            return False
    
    # ==================== WINDOW MANAGEMENT ====================
    def switch_to_new_window(self):
        """Switch to newest window"""
        windows = self.dr.window_handles
        if len(windows) > 1:
            self.dr.switch_to.window(windows[-1])
            if self.verbose: print(f'[WINDOW] Switched to: {self.dr.title}')
    
    # ==================== LOGGING ====================
    def _log_success(self, sel: str, method: str, duration: float):
        self._logs.append({'selector': sel, 'method': method, 'status': 'ok',
                          'duration': round(duration, 3), 'frame': self.frame_path,
                          'url': self.dr.current_url, 'time': time.time()})
        # Auto-flush to prevent memory leak
        if len(self._logs) >= 500:
            self._flush_logs()
    
    def _log_failure(self, sel: str, method: str, duration: float):
        self._logs.append({'selector': sel, 'method': method, 'status': 'fail',
                          'duration': round(duration, 3), 'frame': self.frame_path,
                          'url': self.dr.current_url, 'time': time.time()})
        # Auto-flush to prevent memory leak
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
        if self.verbose: print(f'[LOG] Saved {len(self._logs)} entries to {self.log_path}')
        self._logs.clear()
    
    def save_logs(self):
        """Manually flush logs"""
        self._flush_logs()
    
    def get_stats(self) -> Dict:
        """Get error statistics"""
        return dict(self._error_counts)

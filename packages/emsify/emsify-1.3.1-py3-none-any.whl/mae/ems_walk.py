
from typing import List, Tuple, Union
import time
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException,
    ElementNotInteractableException, StaleElementReferenceException,
    NoAlertPresentException, WebDriverException
)

class SuccessException(Exception):
    pass

class EmsWalk:
    _SE_ERRORS = [
        SuccessException,
        TimeoutException,
        NoSuchElementException,
        ElementClickInterceptedException,
        ElementNotInteractableException,
        StaleElementReferenceException,
        NoAlertPresentException,
        WebDriverException
    ]

    def _handle(self, err: Exception) -> int:
        for i, exc in enumerate(self._SE_ERRORS):
            if isinstance(err, exc):
                print(f"[ERR-{i}] {exc.__name__}: {err}")
                return i
        print(f"[ERR-{len(self._SE_ERRORS)}] Unknown: {err}")
        return -1

    def _guard(fn):
        def _wrap(self, *a, **k):
            try:
                return fn(self, *a, **k)
            except Exception as e:
                return self._handle(e)
        return _wrap

    def __init__(self, driver, max_depth: int = 10):
        self.dr = driver
        self.last_state = 0
        self.error_log = defaultdict(list)
        self.success_log = defaultdict(list)
        self.driver_state = None
        self.max_depth = max_depth
        self._start_time = 0
        self._timeout_budget = 0
        print('EmsWalk access title', self.dr.title)

    def _by(self, sel: str) -> Tuple[str, str]:
        if sel.startswith(("//", "./", "(")): return By.XPATH, sel
        if sel.startswith("xpath="): return By.XPATH, sel[6:]
        if sel.startswith("id="): return By.ID, sel[3:]
        if sel.startswith("name="): return By.NAME, sel[5:]
        if sel.startswith("css="): return By.CSS_SELECTOR, sel[4:]
        return By.CSS_SELECTOR, sel

    @_guard
    def wait_for_clickable(self, sel: str, t: int = 10) -> WebElement:
        by, loc = self._by(sel)
        return WebDriverWait(self.dr, t).until(EC.element_to_be_clickable((by, loc)))

    @_guard
    def wait_for_visible(self, sel: str, t: int = 10) -> WebElement:
        by, loc = self._by(sel)
        return WebDriverWait(self.dr, t).until(EC.visibility_of_element_located((by, loc)))

    @_guard
    def wait_for_present(self, sel: str, t: int = 10) -> WebElement:
        by, loc = self._by(sel)
        return WebDriverWait(self.dr, t).until(EC.presence_of_element_located((by, loc)))

    def _try_wait(self, sel: str, t: int, fn: str):
        r = getattr(self, fn)(sel, t)
        if isinstance(r, WebElement):
            self.last_state = 0
            self.success_log[sel].append(r)
            return r
        else:
            self.last_state = r
            self.error_log[sel].append(r)
            return None

    def _walk_frames(self, sel: str, t: int, fn: str, depth: int = 0):
        if depth >= self.max_depth:
            return None
        if time.time() - self._start_time >= self._timeout_budget:
            return None
        
        frames = self.dr.find_elements(By.CSS_SELECTOR, 'frame,iframe')
        for fr in frames:
            try:
                self.dr.switch_to.frame(fr)
            except StaleElementReferenceException:
                continue
            
            remaining = max(0.5, self._timeout_budget - (time.time() - self._start_time))
            elem = self._try_wait(sel, min(t, remaining), fn)
            if isinstance(elem, WebElement):
                return elem
            
            elem = self._walk_frames(sel, t, fn, depth + 1)
            if isinstance(elem, WebElement):
                return elem
            
            try:
                self.dr.switch_to.parent_frame()
            except:
                self.dr.switch_to.default_content()
        return None

    def locate_element(self, sel: str, t: int = 5, func: str = 'wait_for_visible', default_first: bool = True):
        '''
        default_first = True:
        - last valid locator place -> switch to default -> check in default -> walk frames -> switch to default -> check in default
        default_first = False:
        - last valid locator place -> switch to default -> walk frames -> switch to default -> check in default
        '''
        self._start_time = time.time()
        self._timeout_budget = t * 2
        
        elem = self._try_wait(sel, min(t, 2), func)
        if isinstance(elem, WebElement):
            return elem
        
        print(sel, ' - switching to default - 1st ')
        self.dr.switch_to.default_content()
        
        if default_first:
            remaining = self._timeout_budget - (time.time() - self._start_time)
            if remaining > 0.5:
                elem = self._try_wait(sel, min(t, remaining), func)
                if isinstance(elem, WebElement): return elem
        
        remaining = self._timeout_budget - (time.time() - self._start_time)
        if remaining > 0.5:
            elem = self._walk_frames(sel, t, func)
            if elem: return elem
        
        print(sel, ' - switching to default - 2nd ')
        self.dr.switch_to.default_content()
        remaining = self._timeout_budget - (time.time() - self._start_time)
        if remaining > 0.5:
            elem = self._try_wait(sel, min(t, remaining), func)
            if isinstance(elem, WebElement): return elem
        
        print(sel, ' - locate element failed')
        return None

    def _try_js(self, sel: str, t: int = 5, check_visibility: bool = True) -> Union[WebElement, None]:
        by, loc = self._by(sel)
        start_time = time.time()
        while time.time() - start_time < t:
            try:
                if by == By.XPATH:
                    js_script = """
                    var xpath = arguments[0];
                    var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (result) {
                        var scroller = result;
                        while (scroller && scroller !== document.body) {
                            var style = window.getComputedStyle(scroller);
                            if (style.overflow === 'auto' || style.overflow === 'scroll' || style.overflowY === 'auto' || style.overflowY === 'scroll') {
                                break;
                            }
                            scroller = scroller.parentElement;
                        }
                        if (scroller) {
                            scroller.scrollIntoView({behavior: 'smooth', block: 'center'});
                        }
                        result.scrollIntoView({behavior: 'smooth', block: 'center'});
                        if (arguments[1] && (result.offsetParent === null || window.getComputedStyle(result).display === 'none')) {
                            return null;
                        }
                        return result;
                    }
                    return null;
                    """
                else:
                    js_script = """
                    var selector = arguments[0];
                    var result = document.querySelector(selector);
                    if (result) {
                        var scroller = result;
                        while (scroller && scroller !== document.body) {
                            var style = window.getComputedStyle(scroller);
                            if (style.overflow === 'auto' || style.overflow === 'scroll' || style.overflowY === 'auto' || style.overflowY === 'scroll') {
                                break;
                            }
                            scroller = scroller.parentElement;
                        }
                        if (scroller) {
                            scroller.scrollIntoView({behavior: 'smooth', block: 'center'});
                        }
                        result.scrollIntoView({behavior: 'smooth', block: 'center'});
                        if (arguments[1] && (result.offsetParent === null || window.getComputedStyle(result).display === 'none')) {
                            return null;
                        }
                        return result;
                    }
                    return null;
                    """
                elem = self.dr.execute_script(js_script, loc, check_visibility)
                if elem:
                    self.last_state = 0
                    self.success_log[sel].append(elem)
                    return elem
            except Exception as e:
                err_code = self._handle(e)
                self.error_log[sel].append(err_code)
                self.last_state = err_code
            time.sleep(0.5)
        return None

    def locate_element_js(self, sel: str, t: int = 5, default_first: bool = True, check_visibility: bool = True):
        self._start_time = time.time()
        self._timeout_budget = t * 2
        
        elem = self._try_js(sel, min(t, 2), check_visibility)
        if isinstance(elem, WebElement):
            return elem
        
        print(sel, ' - switching to default - 1st ')
        self.dr.switch_to.default_content()
        
        if default_first:
            remaining = self._timeout_budget - (time.time() - self._start_time)
            if remaining > 0.5:
                elem = self._try_js(sel, min(t, remaining), check_visibility)
                if isinstance(elem, WebElement): return elem
        
        def _walk_frames_js(depth=0):
            if depth >= self.max_depth:
                return None
            if time.time() - self._start_time >= self._timeout_budget:
                return None
            
            frames = self.dr.find_elements(By.CSS_SELECTOR, 'frame,iframe')
            for fr in frames:
                try:
                    self.dr.switch_to.frame(fr)
                except StaleElementReferenceException:
                    continue
                
                remaining = max(0.5, self._timeout_budget - (time.time() - self._start_time))
                elem = self._try_js(sel, min(t, remaining), check_visibility)
                if isinstance(elem, WebElement):
                    return elem
                
                elem = _walk_frames_js(depth + 1)
                if isinstance(elem, WebElement):
                    return elem
                
                try:
                    self.dr.switch_to.parent_frame()
                except:
                    self.dr.switch_to.default_content()
            return None
        
        remaining = self._timeout_budget - (time.time() - self._start_time)
        if remaining > 0.5:
            elem = _walk_frames_js()
            if elem: return elem
        
        print(sel, ' - switching to default - 2nd ')
        self.dr.switch_to.default_content()
        remaining = self._timeout_budget - (time.time() - self._start_time)
        if remaining > 0.5:
            elem = self._try_js(sel, min(t, remaining), check_visibility)
            if isinstance(elem, WebElement): return elem
        
        print(sel, ' - locate element failed (JS)')
        return None


class FrameTracker:
    """
    Mix-in that mirrors every frame jump the driver makes.
    It **does not** know anything about waits, locators, JS, etc.
    """
    # ------------------------------------------------------------------ #
    # public helpers                                                     #
    # ------------------------------------------------------------------ #
    @property
    def ctx_path(self) -> str:
        """Human-readable frame path (default_content if empty)."""
        if not self._frame_stack:
            return "[default_content]"
        names, _ = [], self._frame_stack        # local alias
        for fr in _:
            nm = (isinstance(fr, str) and fr) \
                 or fr.get_attribute("name") \
                 or fr.get_attribute("id") \
                 or f"<idx:{_.index(fr)}>"
            names.append(nm)
        return " > ".join(names)

    # ------------------------------------------------------------------ #
    #  Hook-ins that wrap Selenium switching                             #
    # ------------------------------------------------------------------ #
    def _switch_default(self):
        self.dr.switch_to.default_content()
        self._frame_stack.clear()
        if self._verbose:
            print("[CTX] default_content")

    def _switch_parent(self):
        self.dr.switch_to.parent_frame()
        if self._frame_stack:
            self._frame_stack.pop()
        if self._verbose:
            print(f"[CTX] parent → {self.ctx_path}")

    def _switch_into(self, frame):
        """Call instead of plain driver.switch_to.frame(frame)."""
        self.dr.switch_to.frame(frame)
        self._frame_stack.append(frame)
        if self._verbose:
            print(f"[CTX] into  → {self.ctx_path}")

    # ------------------------------------------------------------------ #
    # internal / dunder                                                  #
    # ------------------------------------------------------------------ #
    def __init__(self, *a, verbose: bool = True, **k):
        super().__init__(*a, **k)          # call next class in MRO
        self._frame_stack: list = []       # holds WebElement refs
        self._verbose     = verbose

class TrackedEmsWalk(FrameTracker, EmsWalk):
    """
    EmsWalk + automatic frame-path tracking.
    Order of bases = (FrameTracker first)  so its __init__
    runs *before* EmsWalk.__init__().
    """

    def __init__(self, driver, max_depth: int = 10, **opts):
        FrameTracker.__init__(self, driver, **opts)
        EmsWalk.__init__(self, driver, max_depth=max_depth, **opts)

    # ---------------------------------------------------------------
    # Override every raw switch with the wrapped versions
    # ---------------------------------------------------------------
    def _walk_frames(self, sel: str, t: int, fn: str, depth: int = 0):
        """Overrides EmsWalk._walk_frames to use tracking."""
        if depth >= self.max_depth:
            return None
        if time.time() - self._start_time >= self._timeout_budget:
            return None
        
        frames = self.dr.find_elements(By.CSS_SELECTOR, 'frame,iframe')
        for fr in frames:
            try:
                self._switch_into(fr)
            except StaleElementReferenceException:
                continue
            
            remaining = max(0.5, self._timeout_budget - (time.time() - self._start_time))
            elem = self._try_wait(sel, min(t, remaining), fn)
            if isinstance(elem, WebElement):
                return elem
            
            elem = self._walk_frames(sel, t, fn, depth + 1)
            if isinstance(elem, WebElement):
                return elem
            
            try:
                self._switch_parent()
            except:
                self._switch_default()
        return None

    # 1) in locate_element()
    def locate_element(self, sel, t=5, func='wait_for_visible', default_first=True):
        self._start_time = time.time()
        self._timeout_budget = t * 2
        
        self._announce(f"🔍 locate_element  sel='{sel}'  ctx={self.ctx_path}")
        elem = self._try_wait(sel, min(t, 2), func)
        if elem: return elem

        self._announce("… switching to default (1st)")
        self._switch_default()

        if default_first:
            remaining = self._timeout_budget - (time.time() - self._start_time)
            if remaining > 0.5:
                elem = self._try_wait(sel, min(t, remaining), func)
                if elem: return elem

        remaining = self._timeout_budget - (time.time() - self._start_time)
        if remaining > 0.5:
            elem = self._walk_frames(sel, t, func)
            if elem: return elem

        self._announce("… switching to default (2nd)")
        self._switch_default()
        remaining = self._timeout_budget - (time.time() - self._start_time)
        if remaining > 0.5:
            elem = self._try_wait(sel, min(t, remaining), func)
            if elem: return elem

        self._announce("locate_element FAILED")
        return None

    # 2) Same override for locate_element_js()
    def locate_element_js(self, sel, t=5, default_first=True, check_visibility=True):
        self._start_time = time.time()
        self._timeout_budget = t * 2
        
        self._announce(f"locate_element_js  sel='{sel}'  ctx={self.ctx_path}")
        elem = self._try_js(sel, min(t, 2), check_visibility)
        if elem: return elem

        self._announce("… switching to default (1st)")
        self._switch_default()

        if default_first:
            remaining = self._timeout_budget - (time.time() - self._start_time)
            if remaining > 0.5:
                elem = self._try_js(sel, min(t, remaining), check_visibility)
                if elem: return elem

        def _walk_frames_js(depth=0):
            if depth >= self.max_depth:
                return None
            if time.time() - self._start_time >= self._timeout_budget:
                return None
            
            frames = self.dr.find_elements(By.CSS_SELECTOR, 'frame,iframe')
            for fr in frames:
                try:
                    self._switch_into(fr)
                except StaleElementReferenceException:
                    continue
                
                remaining = max(0.5, self._timeout_budget - (time.time() - self._start_time))
                elem = self._try_js(sel, min(t, remaining), check_visibility)
                if elem: return elem
                
                elem = _walk_frames_js(depth + 1)
                if elem: return elem
                
                try:
                    self._switch_parent()
                except:
                    self._switch_default()
            return None

        remaining = self._timeout_budget - (time.time() - self._start_time)
        if remaining > 0.5:
            elem = _walk_frames_js()
            if elem: return elem

        self._announce("… switching to default (2nd)")
        self._switch_default()
        remaining = self._timeout_budget - (time.time() - self._start_time)
        if remaining > 0.5:
            elem = self._try_js(sel, min(t, remaining), check_visibility)
            if elem: return elem

        self._announce("locate_element_js FAILED")
        return None

    # ---------------------------------------------------------------
    # Small helper for conditional console prints
    # ---------------------------------------------------------------
    def _announce(self, msg: str):
        if self._verbose:
            print(msg)





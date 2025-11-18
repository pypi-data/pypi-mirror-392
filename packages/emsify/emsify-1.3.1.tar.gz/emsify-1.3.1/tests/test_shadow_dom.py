"""Test Shadow DOM integration"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Suppress atexit warnings
import atexit
atexit._clear = lambda: None

def test_shadow_locate_js():
    """Test Shadow DOM JavaScript function"""
    from mae.ems_automation import EmsAutomation
    
    # Mock driver
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test Page'
        current_url = 'http://test.com'
        
        def execute_script(self, js, *args):
            # Simulate finding element in shadow DOM
            if 'findInShadow' in js and args[0] == '#shadow-button':
                return {'tag': 'button', 'id': 'shadow-button'}
            return None
    
    ems = EmsAutomation(MockDriver(), verbose=False)
    result = ems._locate_shadow('#shadow-button', timeout=1)
    assert result is not None, "Should find element in shadow DOM"
    print("[OK] Shadow DOM locate works")

def test_shadow_parameter():
    """Test shadow parameter in locate method"""
    from mae.ems_automation import EmsAutomation
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test Page'
        current_url = 'http://test.com'
        
        def execute_script(self, js, *args):
            if 'findInShadow' in js:
                return {'found': True}
            return None
    
    ems = EmsAutomation(MockDriver(), verbose=False)
    elem = ems.locate('#test', timeout=1, shadow=True)
    assert elem is not None, "Shadow locate should work"
    print("[OK] Shadow parameter works")

def test_search_both():
    """Test search_both parameter"""
    from mae.ems_automation import EmsAutomation
    from selenium.webdriver.common.by import By
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test Page'
        current_url = 'http://test.com'
        call_count = 0
        
        def switch_to(self):
            return self
        
        def default_content(self):
            pass
        
        def find_elements(self, by, selector):
            return []  # No frames
        
        def execute_script(self, js, *args):
            self.call_count += 1
            # Simulate finding in shadow DOM on 2nd attempt
            if 'findInShadow' in js and self.call_count >= 2:
                return {'found': 'in_shadow'}
            return None
    
    driver = MockDriver()
    driver.switch_to = driver.switch_to()
    ems = EmsAutomation(driver, verbose=False)
    elem = ems.locate('#test', timeout=1, search_both=True)
    assert elem is not None, "search_both should find element"
    assert driver.call_count >= 2, "Should try regular DOM then Shadow DOM"
    print("[OK] search_both parameter works")

if __name__ == '__main__':
    test_shadow_locate_js()
    test_shadow_parameter()
    test_search_both()
    print("\n[PASS] All Shadow DOM tests passed!")

"""Test interact() method"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import atexit
atexit._clear = lambda: None

def test_interact_click():
    """Test interact with click command"""
    from mae.ems_automation import EmsAutomation
    
    class MockElement:
        clicked = False
        def click(self):
            self.clicked = True
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    elem = MockElement()
    ems.locate = lambda sel, timeout, **kw: elem
    
    result = ems.interact('//button', 'click')
    assert result is True
    assert elem.clicked
    print("[OK] interact click works")

def test_interact_send_keys():
    """Test interact with send_keys command"""
    from mae.ems_automation import EmsAutomation
    
    class MockElement:
        text_sent = None
        def send_keys(self, text):
            self.text_sent = text
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    elem = MockElement()
    ems.locate = lambda sel, timeout, **kw: elem
    
    result = ems.interact('id=input', 'send_keys', 'test text')
    assert result is True
    assert elem.text_sent == 'test text'
    print("[OK] interact send_keys works")

def test_interact_get_text():
    """Test interact with get_text command"""
    from mae.ems_automation import EmsAutomation
    
    class MockElement:
        text = 'Hello World'
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    elem = MockElement()
    ems.locate = lambda sel, timeout, **kw: elem
    
    result = ems.interact('//div', 'get_text')
    assert result == 'Hello World'
    print("[OK] interact get_text works")

def test_interact_get_attr():
    """Test interact with get_attr command"""
    from mae.ems_automation import EmsAutomation
    
    class MockElement:
        def get_attribute(self, attr):
            return 'http://example.com' if attr == 'href' else None
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    elem = MockElement()
    ems.locate = lambda sel, timeout, **kw: elem
    
    result = ems.interact('//a', 'get_attr', 'href')
    assert result == 'http://example.com'
    print("[OK] interact get_attr works")

def test_interact_element_not_found():
    """Test interact when element not found"""
    from mae.ems_automation import EmsAutomation
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    ems.locate = lambda sel, timeout, **kw: None
    
    result = ems.interact('//nonexistent', 'click')
    assert result is False
    print("[OK] interact handles missing element")

def test_interact_unknown_command():
    """Test interact with unknown command"""
    from mae.ems_automation import EmsAutomation
    
    class MockElement:
        pass
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    elem = MockElement()
    ems.locate = lambda sel, timeout, **kw: elem
    
    result = ems.interact('//div', 'invalid_command')
    assert result is False
    print("[OK] interact handles unknown command")

if __name__ == '__main__':
    test_interact_click()
    test_interact_send_keys()
    test_interact_get_text()
    test_interact_get_attr()
    test_interact_element_not_found()
    test_interact_unknown_command()
    print("\n[PASS] All interact() tests passed!")

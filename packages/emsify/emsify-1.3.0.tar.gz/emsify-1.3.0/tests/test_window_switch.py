"""Test window switch detection and frame stack reset"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import atexit
atexit._clear = lambda: None

def test_window_switch_detection():
    """Test that window switch is detected"""
    from mae.ems_automation import EmsAutomation
    
    class MockDriver:
        current_window_handle = 'window1'
        title = 'Test Page'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    
    # Initial window
    assert ems._current_window == 'window1'
    
    # Simulate window switch
    driver.current_window_handle = 'window2'
    ems._check_window_switch()
    
    # Should detect switch and update
    assert ems._current_window == 'window2'
    print("[OK] Window switch detected")

def test_frame_stack_reset_on_switch():
    """Test that frame stack is cleared on window switch"""
    from mae.ems_automation import EmsAutomation
    
    class MockFrame:
        def get_attribute(self, attr):
            return 'test-frame'
    
    class MockDriver:
        current_window_handle = 'window1'
        title = 'Test Page'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    
    # Add frames to stack
    ems._frame_stack.append(MockFrame())
    ems._frame_stack.append(MockFrame())
    assert len(ems._frame_stack) == 2
    
    # Simulate window switch
    driver.current_window_handle = 'window2'
    ems._check_window_switch()
    
    # Frame stack should be cleared
    assert len(ems._frame_stack) == 0
    print("[OK] Frame stack reset on window switch")

def test_switch_to_new_window():
    """Test switching to newest window"""
    from mae.ems_automation import EmsAutomation
    
    class MockFrame:
        def get_attribute(self, attr):
            return 'frame1'
    
    class MockSwitchTo:
        def __init__(self, driver):
            self.driver = driver
        
        def window(self, handle):
            self.driver.current_window_handle = handle
    
    class MockDriver:
        current_window_handle = 'window1'
        title = 'Main Window'
        current_url = 'http://test.com'
        window_handles = ['window1', 'window2', 'window3']
        
        def __init__(self):
            self.switch_to = MockSwitchTo(self)
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    
    # Add frame to stack
    ems._frame_stack.append(MockFrame())
    assert len(ems._frame_stack) == 1
    
    # Switch to new window
    ems.switch_to_new_window()
    
    # Should switch to last window
    assert driver.current_window_handle == 'window3'
    assert ems._current_window == 'window3'
    
    # Frame stack should be cleared
    assert len(ems._frame_stack) == 0
    print("[OK] switch_to_new_window works")

def test_no_switch_same_window():
    """Test that no action taken if window hasn't changed"""
    from mae.ems_automation import EmsAutomation
    
    class MockFrame:
        def get_attribute(self, attr):
            return 'frame1'
    
    class MockDriver:
        current_window_handle = 'window1'
        title = 'Test Page'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    
    # Add frame to stack
    ems._frame_stack.append(MockFrame())
    assert len(ems._frame_stack) == 1
    
    # Check window (no change)
    ems._check_window_switch()
    
    # Frame stack should remain
    assert len(ems._frame_stack) == 1
    assert ems._current_window == 'window1'
    print("[OK] No action when window unchanged")

if __name__ == '__main__':
    test_window_switch_detection()
    test_frame_stack_reset_on_switch()
    test_switch_to_new_window()
    test_no_switch_same_window()
    print("\n[PASS] All Window Switch tests passed!")

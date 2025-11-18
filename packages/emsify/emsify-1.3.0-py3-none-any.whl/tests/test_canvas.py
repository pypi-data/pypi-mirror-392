"""Test Canvas interaction methods"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import atexit
atexit._clear = lambda: None

def test_find_canvas():
    """Test finding canvas element"""
    from mae.ems_automation import EmsAutomation
    
    class MockCanvas:
        tag_name = 'canvas'
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test Page'
        current_url = 'http://test.com'
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    
    # Mock locate to return canvas
    ems.locate = lambda sel, timeout: MockCanvas()
    
    canvas = ems.find_canvas('canvas', timeout=1)
    assert canvas is not None, "Should find canvas element"
    assert canvas.tag_name == 'canvas', "Should be canvas element"
    print("[OK] find_canvas works")

def test_click_canvas():
    """Test clicking canvas at coordinates"""
    from mae.ems_automation import EmsAutomation
    
    class MockCanvas:
        tag_name = 'canvas'
        clicked = False
        click_x = None
        click_y = None
    
    class MockActionChains:
        def __init__(self, driver):
            self.driver = driver
            self.canvas = None
            self.x = None
            self.y = None
        
        def move_to_element_with_offset(self, element, x, y):
            self.canvas = element
            self.x = x
            self.y = y
            return self
        
        def click(self):
            return self
        
        def perform(self):
            if self.canvas:
                self.canvas.clicked = True
                self.canvas.click_x = self.x
                self.canvas.click_y = self.y
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test Page'
        current_url = 'http://test.com'
        canvas = MockCanvas()
    
    # Patch ActionChains
    import mae.ems_automation
    original_ac = mae.ems_automation.ActionChains
    mae.ems_automation.ActionChains = MockActionChains
    
    try:
        driver = MockDriver()
        ems = EmsAutomation(driver, verbose=False)
        
        # Mock locate to return canvas
        ems.locate = lambda sel, timeout: driver.canvas
        
        success = ems.click_canvas('canvas', 100, 200, timeout=1)
        assert success, "Should click canvas successfully"
        assert driver.canvas.clicked, "Canvas should be clicked"
        assert driver.canvas.click_x == 100, "X coordinate should match"
        assert driver.canvas.click_y == 200, "Y coordinate should match"
        print("[OK] click_canvas works")
    finally:
        mae.ems_automation.ActionChains = original_ac

def test_get_canvas_data():
    """Test getting canvas image data"""
    from mae.ems_automation import EmsAutomation
    
    class MockCanvas:
        tag_name = 'canvas'
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test Page'
        current_url = 'http://test.com'
        
        def execute_script(self, js, *args):
            if 'toDataURL' in js:
                return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA'
            return None
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    
    # Mock locate to return canvas
    ems.locate = lambda sel, timeout: MockCanvas()
    
    data = ems.get_canvas_data('canvas', timeout=1)
    assert data is not None, "Should get canvas data"
    assert data.startswith('data:image/png'), "Should be PNG data URL"
    print("[OK] get_canvas_data works")

def test_get_canvas_pixel():
    """Test getting pixel color from canvas"""
    from mae.ems_automation import EmsAutomation
    
    class MockCanvas:
        tag_name = 'canvas'
    
    class MockDriver:
        current_window_handle = 'main'
        title = 'Test Page'
        current_url = 'http://test.com'
        
        def execute_script(self, js, *args):
            if 'getImageData' in js:
                # Return RGBA values [255, 128, 64, 255]
                return [255, 128, 64, 255]
            return None
    
    driver = MockDriver()
    ems = EmsAutomation(driver, verbose=False)
    
    # Mock locate to return canvas
    ems.locate = lambda sel, timeout: MockCanvas()
    
    pixel = ems.get_canvas_pixel('canvas', 50, 75, timeout=1)
    assert pixel is not None, "Should get pixel data"
    assert pixel == (255, 128, 64, 255), "Pixel RGBA should match"
    print("[OK] get_canvas_pixel works")

if __name__ == '__main__':
    test_find_canvas()
    test_click_canvas()
    test_get_canvas_data()
    test_get_canvas_pixel()
    print("\n[PASS] All Canvas tests passed!")

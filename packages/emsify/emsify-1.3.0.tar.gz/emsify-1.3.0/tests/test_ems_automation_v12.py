"""
Test EmsAutomation v1.2 refactored architecture
"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from unittest.mock import Mock, MagicMock, patch
from selenium.webdriver.remote.webelement import WebElement


class TestEmsAutomationV12Architecture:
    """Test that v1.2 properly inherits from TrackedEmsWalk"""
    
    @pytest.fixture
    def mock_driver(self):
        driver = Mock()
        driver.title = "Test EMS Portal"
        driver.current_url = "https://ems.example.com"
        driver.window_handles = ["window1"]
        return driver
    
    def test_imports_trackedems_walk(self):
        """Should import TrackedEmsWalk"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, 'TrackedEmsWalk')
    
    def test_inherits_from_tracked_ems_walk(self, mock_driver):
        """Should inherit from TrackedEmsWalk"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        assert isinstance(ems, module.TrackedEmsWalk)
    
    def test_has_max_depth_parameter(self, mock_driver):
        """Should accept max_depth parameter"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, max_depth=5, verbose=False)
        assert ems.max_depth == 5
    
    def test_has_validate_path_parameter(self, mock_driver):
        """Should accept validate_path parameter"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, validate_path=False, verbose=False)
        assert ems.validate_path == False
    
    def test_has_ctx_path_from_parent(self, mock_driver):
        """Should have ctx_path property from TrackedEmsWalk"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        assert hasattr(ems, 'ctx_path')
        assert ems.ctx_path == "[default_content]"
    
    def test_has_frame_stack_from_parent(self, mock_driver):
        """Should have _frame_stack from TrackedEmsWalk"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        assert hasattr(ems, '_frame_stack')
        assert isinstance(ems._frame_stack, list)
    
    def test_locate_delegates_to_parent(self, mock_driver):
        """locate() should delegate to parent class methods"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        mock_element = Mock(spec=WebElement)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        with patch.object(ems, 'locate_element', return_value=mock_element) as mock_locate:
            result = ems.locate('//button', timeout=5, method='selenium')
            mock_locate.assert_called_once()
            assert result == mock_element
    
    def test_locate_js_delegates_to_parent(self, mock_driver):
        """locate() with method='js' should delegate to locate_element_js"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        mock_element = Mock(spec=WebElement)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        with patch.object(ems, 'locate_element_js', return_value=mock_element) as mock_locate_js:
            result = ems.locate('//button', timeout=5, method='js')
            mock_locate_js.assert_called_once()
            assert result == mock_element


class TestInputValidation:
    """Test input validation in v1.2"""
    
    @pytest.fixture
    def mock_driver(self):
        driver = Mock()
        driver.title = "Test"
        driver.current_url = "https://test.com"
        return driver
    
    def test_locate_validates_empty_selector(self, mock_driver):
        """Should reject empty selector"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        with pytest.raises(ValueError, match="Invalid selector"):
            ems.locate('')
    
    def test_locate_validates_none_selector(self, mock_driver):
        """Should reject None selector"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        with pytest.raises(ValueError, match="Invalid selector"):
            ems.locate(None)
    
    def test_locate_validates_negative_timeout(self, mock_driver):
        """Should reject negative timeout"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        with pytest.raises(ValueError, match="Timeout must be positive"):
            ems.locate('//button', timeout=-1)
    
    def test_locate_validates_zero_timeout(self, mock_driver):
        """Should reject zero timeout"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        with pytest.raises(ValueError, match="Timeout must be positive"):
            ems.locate('//button', timeout=0)


class TestPathValidationInUpload:
    """Test path validation in upload_file"""
    
    @pytest.fixture
    def mock_driver(self):
        driver = Mock()
        driver.title = "Test"
        driver.current_url = "https://test.com"
        return driver
    
    def test_upload_validates_path_by_default(self, mock_driver):
        """Should validate file path by default"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False, validate_path=True)
        
        with pytest.raises(ValueError, match="Path outside allowed directory"):
            ems.upload_file("../../../etc/passwd", "//input")
    
    def test_upload_skips_validation_when_disabled(self, mock_driver):
        """Should skip validation when disabled"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False, validate_path=False)
        
        # Should not raise ValueError (will fail on file not found, which is ok)
        result = ems.upload_file("../../../nonexistent", "//input")
        assert result == False  # File doesn't exist, but no ValueError


class TestErrorTracking:
    """Test error tracking improvements"""
    
    @pytest.fixture
    def mock_driver(self):
        driver = Mock()
        driver.title = "Test"
        driver.current_url = "https://test.com"
        return driver
    
    def test_tracks_errors(self, mock_driver):
        """Should track errors in _error_counts"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        error = ValueError("test error")
        ems._handle_error(error, "test context")
        
        assert "ValueError" in ems._error_counts
        assert ems._error_counts["ValueError"] == 1
    
    def test_get_stats_returns_errors(self, mock_driver):
        """get_stats() should return error counts"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        ems._handle_error(ValueError("test1"), "ctx1")
        ems._handle_error(ValueError("test2"), "ctx2")
        ems._handle_error(TypeError("test3"), "ctx3")
        
        stats = ems.get_stats()
        assert stats["ValueError"] == 2
        assert stats["TypeError"] == 1


class TestLogging:
    """Test logging functionality"""
    
    @pytest.fixture
    def mock_driver(self):
        driver = Mock()
        driver.title = "Test"
        driver.current_url = "https://test.com"
        return driver
    
    def test_uses_ctx_path_in_logs(self, mock_driver):
        """Should use ctx_path from parent class in logs"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        ems._log_success('//button', 'selenium', 1.5)
        
        assert len(ems._logs) == 1
        assert ems._logs[0]['frame'] == "[default_content]"
    
    def test_auto_flush_at_500(self, mock_driver):
        """Should auto-flush logs at 500 entries"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("ems_automation_v12", "mae/ems_automation_v1.2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ems = module.EmsAutomation(mock_driver, verbose=False)
        
        with patch.object(ems, '_flush_logs') as mock_flush:
            for i in range(500):
                ems._log_success(f'//button{i}', 'selenium', 0.1)
            
            mock_flush.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

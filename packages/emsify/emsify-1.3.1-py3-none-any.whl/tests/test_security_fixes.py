"""
Test security fixes: XSS sanitization and path traversal prevention
"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from mae import xpath_builder as xp
from mae.drivers import edge, chrome, firefox


class TestXPathSanitization:
    """Test XSS vulnerability fixes in xpath_builder"""
    
    def test_sanitize_single_quote(self):
        """Should escape single quotes"""
        result = xp._sanitize("admin' or '1'='1")
        assert "&apos;" in result
        assert "admin&apos; or &apos;1&apos;=&apos;1" == result
    
    def test_sanitize_double_quote(self):
        """Should escape double quotes"""
        result = xp._sanitize('test"value')
        assert "&quot;" in result
        assert 'test&quot;value' == result
    
    def test_sanitize_mixed_quotes(self):
        """Should escape both quote types"""
        result = xp._sanitize("""admin's "test" """)
        assert "&apos;" in result
        assert "&quot;" in result
    
    def test_sanitize_disabled(self):
        """Should not sanitize when disabled"""
        result = xp._sanitize("admin' or '1'='1", sanitize=False)
        assert "&apos;" not in result
        assert result == "admin' or '1'='1"
    
    def test_button_with_text_sanitized(self):
        """button_with_text should sanitize by default"""
        xpath = xp.button_with_text("admin' or '1'='1")
        assert "&apos;" in xpath
        assert "//button[normalize-space(text())=\"admin&apos; or &apos;1&apos;=&apos;1\"]" == xpath
    
    def test_button_with_text_unsanitized(self):
        """button_with_text should allow disabling sanitization"""
        xpath = xp.button_with_text("admin's button", sanitize=False)
        assert "&apos;" not in xpath
        assert "//button[normalize-space(text())=\"admin's button\"]" == xpath
    
    def test_input_with_placeholder_sanitized(self):
        """input_with_placeholder should sanitize"""
        xpath = xp.input_with_placeholder('test"value')
        assert "&quot;" in xpath
    
    def test_has_class_sanitized(self):
        """has_class should sanitize"""
        xpath = xp.has_class(xp.xpath('div'), "class'name")
        assert "&apos;" in xpath
    
    def test_contains_text_sanitized(self):
        """contains_text should sanitize"""
        xpath = xp.contains_text(xp.xpath('span'), "text'value")
        assert "&apos;" in xpath
    
    def test_chain_sanitization(self):
        """XPathChain should sanitize"""
        xpath = xp.chain('div').has_class("test'class").text("admin' text").build()
        assert xpath.count("&apos;") == 2


class TestPathTraversal:
    """Test path traversal vulnerability fixes"""
    
    def test_validate_path_safe(self):
        """Should accept paths within current directory"""
        safe_path = "./test_file.txt"
        result = edge._validate_path(safe_path)
        assert isinstance(result, Path)
    
    def test_validate_path_traversal_blocked(self):
        """Should block path traversal attempts"""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32"
        ]
        for path in malicious_paths:
            with pytest.raises(ValueError, match="Path outside allowed directory"):
                edge._validate_path(path)
    
    def test_validate_path_absolute_blocked(self):
        """Should block absolute paths outside cwd"""
        with pytest.raises(ValueError):
            edge._validate_path("/tmp/malicious")
    
    def test_validate_path_subdirectory_allowed(self):
        """Should allow subdirectories"""
        result = edge._validate_path("./subdir/file.txt")
        assert isinstance(result, Path)
    
    def test_edge_download_validates_path(self):
        """Edge driver download should validate path"""
        with pytest.raises(ValueError):
            edge.download_msedgedriver("120.0.0", "../../../tmp", validate_path=True)
    
    def test_edge_download_skip_validation(self):
        """Edge driver download should allow skipping validation"""
        # Should not raise (but will fail on download, which is expected)
        try:
            edge.download_msedgedriver("120.0.0", "../../../tmp", validate_path=False)
        except Exception as e:
            # Any error except ValueError is acceptable (network, file not found, etc.)
            assert not isinstance(e, ValueError)
    
    def test_chrome_download_validates_path(self):
        """Chrome driver download should validate path"""
        with pytest.raises(ValueError):
            chrome.download_chromedriver("120.0.0", "../../../tmp", validate_path=True)
    
    def test_firefox_download_validates_path(self):
        """Firefox driver download should validate path"""
        with pytest.raises(ValueError):
            firefox.download_geckodriver("v0.33.0", "../../../tmp", validate_path=True)


class TestBackwardCompatibility:
    """Test that escape hatches work for backward compatibility"""
    
    def test_xpath_sanitize_false_works(self):
        """Disabling sanitization should work"""
        xpath = xp.button_with_text("test'value", sanitize=False)
        assert "test'value" in xpath
        assert "&apos;" not in xpath
    
    def test_path_validate_false_works(self):
        """Disabling path validation should work via function parameter"""
        # The _validate_path function always validates
        # But download functions have validate_path parameter
        # Test that the parameter exists and can be set to False
        import inspect
        sig = inspect.signature(edge.download_msedgedriver)
        assert 'validate_path' in sig.parameters
        assert sig.parameters['validate_path'].default == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

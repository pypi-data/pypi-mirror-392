# MAE - Modern Automation for EMS

Web scraping toolkit optimized for telecom EMS portals (Huawei, Ericsson, Alcatel).

## Features

- 🎯 **Smart Frame Navigation** - Automatic frame detection and switching
- ⚡ **Dual Location Strategy** - Selenium + JavaScript methods
- 🔄 **Auto-Retry Logic** - Handles dynamic content loading
- 📊 **Error Tracking** - Built-in statistics and logging
- 🛡️ **Stale Frame Protection** - Robust error handling
- 📝 **CSV Logging** - Auto-flush prevents memory leaks

## Installation

### Online Installation
```bash
pip install mae
```

### Offline Installation (Corporate Environments)
```bash
# On machine with internet:
pip download mae -d mae_offline

# Copy mae_offline/ folder to offline machine, then:
cd mae_offline
pip install mae-1.0.0-py3-none-any.whl --no-index --find-links .
```

### Development Installation
```bash
git clone https://github.com/yourusername/mae.git
cd mae
pip install -e .
```

## Quick Start

```python
from selenium import webdriver
from mae import EmsAutomation

driver = webdriver.Edge()
driver.get('https://ems-portal.example.com')

ems = EmsAutomation(driver)

# Login
ems.send_keys('id=username', 'admin')
ems.send_keys('id=password', 'secret')
ems.click('//button[@id="login"]')

# Navigate (handles frames automatically)
ems.hover_click('//div[@class="menu"]', '//a[text()="Settings"]')

# Upload file
ems.upload_file('config.xml', '#dropzone')

# Get statistics
print(ems.get_stats())
```

## Understanding locate() Method

The `locate()` method is the core element finder with smart frame navigation:

```python
# Basic usage - finds element anywhere (current frame, default, or nested frames)
element = ems.locate('//button[@id="submit"]')

# Specify timeout
element = ems.locate('//button', timeout=10)

# Use JavaScript method (faster for hidden elements)
element = ems.locate('#hidden-field', method='js')

# Control search strategy
element = ems.locate('//input', default_first=True)   # Thorough search
element = ems.locate('//input', default_first=False)  # Skip default, faster

# Specify wait condition (selenium method only)
element = ems.locate('//button', condition='clickable')  # Wait until clickable
element = ems.locate('//div', condition='visible')      # Wait until visible
element = ems.locate('//span', condition='present')     # Wait until present
```

**Search Order** (optimized for EMS portals):
1. Current frame (fast - 90% hit rate for sequential operations)
2. Default content (if `default_first=True`)
3. All nested frames (depth-first search)
4. Default content again (final attempt)

**Why it's smart**: If you find 3-4 elements in the same frame, only the first search walks all frames. Subsequent calls are instant.

## Selector Formats

```python
# XPath (starts with // or ./ or ()
ems.locate('//button[@id="submit"]')
ems.locate('.//input[@type="text"]')

# CSS Selector (default)
ems.locate('#submit-button')
ems.locate('.form-control')

# Explicit prefix
ems.locate('xpath=//button[@id="submit"]')
ems.locate('css=#submit-button')
ems.locate('id=submit-button')
ems.locate('name=username')
```

## Documentation

- [Usage Guide](docs/GUIDE.md) - Comprehensive usage examples
- [API Reference](docs/API.md) - Complete API documentation
- [Migration Guide](docs/MIGRATION.md) - Migrate from old scripts
- [Design Documentation](docs/DESIGN.md) - Architecture and design

## Key Advantages

### Smart "Current Context First" Algorithm
```
A) Try current context (90% hit rate for sequential operations)
B) Try default content (if default_first=True)
C) Walk all frames depth-first (thorough search)
D) Final attempt in default (last chance)
```

### Handles Complex EMS Scenarios
- ✅ Nested frames (3-4 levels deep)
- ✅ Dynamic content (async loading)
- ✅ Auto-refreshing frames
- ✅ Hidden elements
- ✅ Image buttons
- ✅ Multiple tabs/windows

## Examples

See [examples/](examples/) for complete working examples:
- `basic_usage.py` - Simple automation
- `ems_portal_login.py` - Real EMS portal workflow
- `migration_example.py` - Migrate from old scripts

## Requirements

- Python >= 3.7
- Selenium >= 4.0.0
- WebDriver executable (see Limitations below)

## Limitations & Solutions

### 1. WebDriver Not Available

**Problem**: Script fails with "WebDriver not found" error.

**Solution**: Download WebDriver manually for offline/corporate environments:

```python
# Option A: Use compatibility utilities (requires internet once)
from mae.drivers import download_chromedriver, download_msedgedriver

# Download once (with internet)
download_msedgedriver('130.0.0.0')  # Your Edge version

# Option B: Manual download (for offline environments)
# 1. Check browser version: edge://version or chrome://version
# 2. Download matching driver:
#    - Edge: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
#    - Chrome: https://googlechromelabs.github.io/chrome-for-testing/
# 3. Place in project folder or system PATH

# Option C: Specify driver path explicitly
from selenium.webdriver.edge.service import Service
service = Service('C:/path/to/msedgedriver.exe')
driver = webdriver.Edge(service=service)
```

### 2. Version Mismatch (Driver vs Browser)

**Problem**: "session not created: This version of ChromeDriver only supports Chrome version X" error.

**Solution**:

```python
# Check versions
from mae.drivers import get_edge_version, get_msedgedriver_version

print(f"Edge: {get_edge_version()}")
print(f"Driver: {get_msedgedriver_version()}")

# If mismatch, download matching driver (requires internet)
from mae.drivers import download_msedgedriver
download_msedgedriver(get_edge_version())
```

**For Corporate/Offline Environments**:
1. On a machine with internet, download correct driver version
2. Copy driver executable to offline machine
3. Place in project folder or add to PATH
4. Specify path explicitly in code

### 3. Corporate Intranet (No Internet)

**Problem**: Cannot auto-download drivers, package dependencies.

**Solution - One-Time Setup**:

```bash
# On machine WITH internet:
# 1. Download package
pip download mae -d mae_offline

# 2. Download WebDriver
# Visit: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
# Download version matching your browser

# 3. Copy to offline machine:
#    - mae_offline/ folder
#    - msedgedriver.exe

# On offline machine:
cd mae_offline
pip install mae-1.0.0-py3-none-any.whl --no-index --find-links .

# Use with explicit driver path
from selenium.webdriver.edge.service import Service
service = Service('./msedgedriver.exe')
driver = webdriver.Edge(service=service)
```

### 4. Frame Detection Issues

**Problem**: Element not found despite being visible.

**Solution**:

```python
# Try JS method (bypasses some frame restrictions)
element = ems.locate('//button', method='js')

# Check current frame context
print(ems.frame_path)  # Shows where you are

# Increase timeout for slow-loading frames
element = ems.locate('//button', timeout=20)

# Use TrackedEmsWalk for debugging
from mae import TrackedEmsWalk
tracked = TrackedEmsWalk(driver, verbose=True)
tracked.locate_element('//button')  # Shows frame switches
```

### 5. Dynamic Content Not Loading

**Problem**: Element appears after delay, script fails.

**Solution**:

```python
# Increase timeout
element = ems.locate('//div[@class="loaded"]', timeout=30)

# Use JS method with retry
element = ems.locate('//div', method='js', timeout=15)

# Wait for specific condition
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="loaded"]'))
)
```

## Troubleshooting

### Check WebDriver Setup
```python
from mae.drivers import get_edge_version, get_msedgedriver_version

print(f"Browser: {get_edge_version()}")
print(f"Driver: {get_msedgedriver_version()}")
# Versions should match (at least major version)
```

### Enable Verbose Mode
```python
ems = EmsAutomation(driver, verbose=True)
# Shows frame switches, errors, and search progress
```

### Check Logs
```python
ems.save_logs()  # Creates CSV with all operations
# Review: {domain}_log.csv
```

## License

MIT License

## Best Practices for Corporate/Offline Environments

1. **Pre-download WebDriver**: Get correct version before going offline
2. **Version Lock**: Document browser and driver versions in requirements
3. **Explicit Paths**: Don't rely on PATH, specify driver location
4. **Test Setup**: Verify driver works before deploying to offline machines
5. **Keep Backup**: Store driver executables in version control or shared drive

```python
# Recommended setup for corporate environments
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from mae import EmsAutomation
import os

# Use relative path to driver in project folder
driver_path = os.path.join(os.path.dirname(__file__), 'msedgedriver.exe')
service = Service(driver_path)
driver = webdriver.Edge(service=service)

ems = EmsAutomation(driver, verbose=True)
```

## Support

For issues and questions, see [docs/](docs/) or check the reference implementations in [reference/](reference/).

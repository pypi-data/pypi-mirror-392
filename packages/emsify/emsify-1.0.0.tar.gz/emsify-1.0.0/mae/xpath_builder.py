"""XPath Builder - Fluent interface for building XPath expressions"""

def xpath(tag: str = '*') -> str:
    """Start building XPath with base tag"""
    return f'//{tag}'

def attr(xpath_str: str, name: str, value: str) -> str:
    """Add attribute condition"""
    return f'{xpath_str}[@{name}="{value}"]'

def contains_attr(xpath_str: str, name: str, value: str) -> str:
    """Add contains attribute condition"""
    return f'{xpath_str}[contains(@{name},"{value}")]'

def text(xpath_str: str, value: str) -> str:
    """Add exact text condition"""
    return f'{xpath_str}[normalize-space(text())="{value}"]'

def contains_text(xpath_str: str, value: str) -> str:
    """Add contains text condition"""
    return f'{xpath_str}[contains(normalize-space(.),"{value}")]'

def has_class(xpath_str: str, class_name: str) -> str:
    """Add class condition"""
    return f'{xpath_str}[contains(@class,"{class_name}")]'

def has_id(xpath_str: str, id_value: str) -> str:
    """Add ID condition"""
    return f'{xpath_str}[@id="{id_value}"]'

# Convenience builders
def button_with_text(text_value: str) -> str:
    """Build button XPath with text"""
    return text(xpath('button'), text_value)

def input_with_placeholder(placeholder_value: str) -> str:
    """Build input XPath with placeholder"""
    return attr(xpath('input'), 'placeholder', placeholder_value)

def link_with_text(text_value: str) -> str:
    """Build link XPath with text"""
    return text(xpath('a'), text_value)

def div_with_class(class_name: str) -> str:
    """Build div XPath with class"""
    return has_class(xpath('div'), class_name)

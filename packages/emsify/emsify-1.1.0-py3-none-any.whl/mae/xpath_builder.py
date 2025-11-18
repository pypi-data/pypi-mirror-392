"""XPath Builder - Fluent interface for building XPath expressions"""

def xpath(tag: str = '*') -> str:
    return f'//{tag}'

def attr(xpath_str: str, name: str, value: str) -> str:
    return f'{xpath_str}[@{name}="{value}"]'

def contains_attr(xpath_str: str, name: str, value: str) -> str:
    return f'{xpath_str}[contains(@{name},"{value}")]'

def text(xpath_str: str, value: str) -> str:
    return f'{xpath_str}[normalize-space(text())="{value}"]'

def contains_text(xpath_str: str, value: str) -> str:
    return f'{xpath_str}[contains(normalize-space(.),"{value}")]'

def child(xpath_str: str, tag: str = '*') -> str:
    return f'{xpath_str}/{tag}'

def descendant(xpath_str: str, tag: str = '*') -> str:
    return f'{xpath_str}//{tag}'

def following_sibling(xpath_str: str, tag: str = '*') -> str:
    return f'{xpath_str}/following-sibling::{tag}'

def preceding_sibling(xpath_str: str, tag: str = '*') -> str:
    return f'{xpath_str}/preceding-sibling::{tag}'

def ancestor(xpath_str: str, tag: str = '*') -> str:
    return f'{xpath_str}/ancestor::{tag}'

def position(xpath_str: str, pos: int) -> str:
    return f'({xpath_str})[{pos}]'

def last(xpath_str: str) -> str:
    return f'({xpath_str})[last()]'

def first(xpath_str: str) -> str:
    return f'({xpath_str})[1]'

def has_class(xpath_str: str, class_name: str) -> str:
    return f'{xpath_str}[contains(@class,"{class_name}")]'

def has_id(xpath_str: str, id_value: str) -> str:
    return f'{xpath_str}[@id="{id_value}"]'

def has_name(xpath_str: str, name_value: str) -> str:
    return f'{xpath_str}[@name="{name_value}"]'

def has_type(xpath_str: str, type_value: str) -> str:
    return f'{xpath_str}[@type="{type_value}"]'

def visible(xpath_str: str) -> str:
    return f'{xpath_str}[not(@style) or not(contains(@style,"display:none")) and not(contains(@style,"visibility:hidden"))]'

def enabled(xpath_str: str) -> str:
    return f'{xpath_str}[not(@disabled)]'

def or_xpath(*xpaths: str) -> str:
    return ' | '.join(xpaths)

# Convenience builders
def button_with_text(text_value: str) -> str:
    return text(xpath('button'), text_value)

def input_with_placeholder(placeholder_value: str) -> str:
    return attr(xpath('input'), 'placeholder', placeholder_value)

def link_with_text(text_value: str) -> str:
    return text(xpath('a'), text_value)

def div_with_class(class_name: str) -> str:
    return has_class(xpath('div'), class_name)

def span_contains_text(text_value: str) -> str:
    return contains_text(xpath('span'), text_value)

# Chaining
class XPathChain:
    def __init__(self, xpath_str: str):
        self._xpath = xpath_str
    
    def attr(self, name: str, value: str):
        self._xpath = attr(self._xpath, name, value)
        return self
    
    def contains_attr(self, name: str, value: str):
        self._xpath = contains_attr(self._xpath, name, value)
        return self
    
    def text(self, value: str):
        self._xpath = text(self._xpath, value)
        return self
    
    def contains_text(self, value: str):
        self._xpath = contains_text(self._xpath, value)
        return self
    
    def child(self, tag: str = '*'):
        self._xpath = child(self._xpath, tag)
        return self
    
    def descendant(self, tag: str = '*'):
        self._xpath = descendant(self._xpath, tag)
        return self
    
    def has_class(self, class_name: str):
        self._xpath = has_class(self._xpath, class_name)
        return self
    
    def has_id(self, id_value: str):
        self._xpath = has_id(self._xpath, id_value)
        return self
    
    def position(self, pos: int):
        self._xpath = position(self._xpath, pos)
        return self
    
    def first(self):
        self._xpath = first(self._xpath)
        return self
    
    def last(self):
        self._xpath = last(self._xpath)
        return self
    
    def visible(self):
        self._xpath = visible(self._xpath)
        return self
    
    def enabled(self):
        self._xpath = enabled(self._xpath)
        return self
    
    def build(self) -> str:
        return self._xpath

def chain(tag: str = '*') -> XPathChain:
    return XPathChain(xpath(tag))

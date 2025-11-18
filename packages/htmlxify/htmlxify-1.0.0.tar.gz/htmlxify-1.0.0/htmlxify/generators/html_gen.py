"""
HTML Generator - Converts AST to secure HTML
Security: All text is HTML-escaped to prevent XSS
"""

import html as html_escape_module
from typing import Dict, Any, List, Tuple
import json


class HTMLGenerator:
    """
    Generates HTML from AST with security features:
    - Automatic HTML escaping
    - XSS prevention
    - Source map generation for debugging
    """
    
    def __init__(self, ast: Dict[str, Any], filename: str):
        self.ast = ast
        self.filename = filename
        self.output: List[str] = []
        self.current_line = 0
    
    def generate(self) -> Tuple[str, str]:
        """
        Generate HTML and source map.
        Returns: (html_string, source_map_json)
        """
        # Start with doctype
        self.output.append('<!DOCTYPE html>\n')
        self.current_line += 1
        
        # Generate from AST
        self._generate_node(self.ast)
        
        # Combine output
        html_code = ''.join(self.output)
        
        # Simple source map (line mappings only)
        source_map = json.dumps({
            "version": 3,
            "file": self.filename.replace('.htmlxify', '.html'),
            "sources": [self.filename],
            "names": [],
            "mappings": ""
        })
        
        return html_code, source_map
    
    def _generate_node(self, node: Any, depth: int = 0):
        """Recursively generate HTML from node"""
        if not isinstance(node, dict):
            return
        
        node_type = node.get('type')
        
        if node_type in ('Document', 'Root'):
            # Generate children
            for child in node.get('children', []):
                self._generate_node(child, depth)
        
        elif node_type == 'Element':
            self._generate_element(node, depth)
        
        elif node_type == 'Text':
            self._generate_text(node)
    
    def _generate_element(self, node: Dict[str, Any], depth: int):
        """Generate HTML element"""
        indent = '  ' * depth
        tag = node.get('tag', 'div')
        
        # Opening tag
        self.output.append(f'{indent}<{tag}')
        
        # ID attribute
        if node.get('id'):
            safe_id = html_escape_module.escape(node['id'], quote=True)
            self.output.append(f' id="{safe_id}"')
        
        # Classes
        if node.get('classes'):
            classes = ' '.join(node['classes'])
            safe_classes = html_escape_module.escape(classes, quote=True)
            self.output.append(f' class="{safe_classes}"')
        
        # Other attributes
        self._generate_attributes(node.get('attributes', {}))
        
        self.output.append('>')
        
        # Children
        has_children = node.get('children')
        if has_children:
            self.output.append('\n')
            self.current_line += 1
            
            for child in has_children:
                self._generate_node(child, depth + 1)
            
            self.output.append(f'{indent}')
        
        # Closing tag
        self.output.append(f'</{tag}>\n')
        self.current_line += 1
    
    def _generate_attributes(self, attrs: Dict[str, Any]):
        """Generate HTML attributes"""
        for key, value in attrs.items():
            if key == '⚡-call':
                # Backend API call - convert to data attribute
                if isinstance(value, dict):
                    endpoint = value.get('endpoint', '')
                else:
                    endpoint = str(value)
                
                safe_endpoint = html_escape_module.escape(endpoint, quote=True)
                self.output.append(f' data-api-call="{safe_endpoint}"')
            
            elif key == '⚡-data':
                # Dynamic data binding - mark for JS
                if isinstance(value, dict):
                    data_key = value.get('key', '')
                else:
                    data_key = str(value)
                
                safe_key = html_escape_module.escape(data_key, quote=True)
                self.output.append(f' data-dynamic="{safe_key}"')
            
            else:
                # Regular attribute
                safe_key = html_escape_module.escape(str(key), quote=True)
                safe_value = html_escape_module.escape(str(value), quote=True)
                self.output.append(f' {safe_key}="{safe_value}"')
    
    def _generate_text(self, node: Dict[str, Any]):
        """Generate text node - ALWAYS ESCAPED"""
        text = node.get('value', '')
        
        # SECURITY: Escape HTML entities to prevent XSS
        safe_text = html_escape_module.escape(text)
        
        self.output.append(safe_text)


# Test
if __name__ == '__main__':
    test_ast = {
        'type': 'Document',
        'children': [
            {
                'type': 'Element',
                'tag': 'div',
                'id': 'container',
                'classes': ['main', 'wrapper'],
                'attributes': {
                    '⚡-call': {'type': 'backend_call', 'endpoint': 'getData'}
                },
                'children': [
                    {
                        'type': 'Element',
                        'tag': 'h1',
                        'id': None,
                        'classes': [],
                        'attributes': {},
                        'children': [
                            {
                                'type': 'Text',
                                'value': 'Hello <script>alert("XSS")</script>'  # Should be escaped
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    gen = HTMLGenerator(test_ast, 'test.htmlxify')
    html, source_map = gen.generate()
    
    print("Generated HTML:")
    print(html)
    print("\nNotice: <script> tag is escaped to &lt;script&gt; - XSS prevented!")

"""
Semantic Validator - Checks AST for errors and warnings
Security: Ensures no emoji identifiers, validates backend calls
"""

import re
from typing import List, Dict, Any, Optional


class ValidationIssue:
    """Represents an error or warning"""
    
    def __init__(
        self,
        node: Dict[str, Any],
        message: str,
        severity: str = 'error',
        line: Optional[int] = None
    ):
        self.node = node
        self.message = message
        self.severity = severity  # 'error' or 'warning'
        self.line = line or node.get('meta', {}).get('line', 0)
    
    def __repr__(self):
        return f"<{self.severity.upper()}: {self.message}>"


class SemanticValidator:
    """
    Validates the AST for:
    - Invalid identifiers (emojis, special characters)
    - Performance anti-patterns
    - Security issues
    - Component naming conventions
    """
    
    # Valid identifier pattern (JavaScript-compatible)
    IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_-]*$')
    
    # Component name pattern (must have hyphen)
    COMPONENT_PATTERN = re.compile(r'^[a-z]+-[a-z-]+$')
    
    def __init__(self, ast: Dict[str, Any], filename: str):
        self.ast = ast
        self.filename = filename
        self.errors: List[ValidationIssue] = []
        self.warnings: List[ValidationIssue] = []
    
    def validate(self) -> bool:
        """
        Run all validation checks.
        Returns True if valid, False if errors found.
        Warnings don't prevent compilation.
        """
        self._walk_ast(self.ast)
        
        # Report issues
        if self.errors:
            self._report_issues('ERRORS', self.errors)
            return False
        
        if self.warnings:
            self._report_issues('WARNINGS', self.warnings)
        
        return True
    
    def _walk_ast(self, node: Any):
        """Recursively walk AST and validate each node"""
        if not isinstance(node, dict):
            return
        
        # Validate this node
        if node.get('type') == 'Element':
            self._validate_element(node)
        elif node.get('type') == 'Text':
            self._validate_text(node)
        
        # Recurse into children
        for child in node.get('children', []):
            self._walk_ast(child)
    
    def _validate_element(self, node: Dict[str, Any]):
        """Validate element node"""
        
        # 1. Validate ID (NO EMOJIS)
        element_id = node.get('id')
        if element_id:
            if not self.IDENTIFIER_PATTERN.match(element_id):
                self.errors.append(ValidationIssue(
                    node,
                    f"Invalid ID '{element_id}'. "
                    f"Use only alphanumeric characters, hyphens, and underscores. "
                    f"Emojis are NOT allowed in identifiers.",
                    severity='error'
                ))
        
        # 2. Validate class names
        for cls in node.get('classes', []):
            if not self.IDENTIFIER_PATTERN.match(cls):
                self.errors.append(ValidationIssue(
                    node,
                    f"Invalid class name '{cls}'. "
                    f"No emojis or special characters allowed.",
                    severity='error'
                ))
        
        # 3. Check component naming
        tag = node.get('tag', '')
        if 'component' in tag.lower() or '-' in tag:
            # This is a custom component
            if not self.COMPONENT_PATTERN.match(tag):
                self.errors.append(ValidationIssue(
                    node,
                    f"Component names must be lowercase with hyphen: '{tag}' → 'my-component'",
                    severity='error'
                ))
        
        # 4. Performance warnings
        self._check_performance(node)
        
        # 5. Security checks
        self._check_security(node)
    
    def _check_performance(self, node: Dict[str, Any]):
        """Check for performance anti-patterns"""
        attrs = node.get('attributes', {})
        
        # Check if animating non-GPU properties
        animate = attrs.get('animate')
        if animate:
            # Warn if animate is defined but might not use GPU
            self.warnings.append(ValidationIssue(
                node,
                "Animation detected. Ensure you use 'transform' and 'opacity' "
                "for GPU acceleration. Avoid animating 'left', 'top', 'width', 'height'.",
                severity='warning'
            ))
        
        # Check inline styles for bad properties
        style = attrs.get('style', '')
        bad_props = ['left', 'top', 'width', 'height']
        
        if isinstance(style, str):
            for prop in bad_props:
                if prop in style.lower():
                    self.warnings.append(ValidationIssue(
                        node,
                        f"Animating '{prop}' causes layout recalculation. "
                        f"Use 'transform' instead for better performance.",
                        severity='warning'
                    ))
    
    def _check_security(self, node: Dict[str, Any]):
        """Check security issues"""
        attrs = node.get('attributes', {})
        
        # Mark nodes with dynamic data for sanitization
        if '⚡-data' in attrs:
            node['_needs_sanitization'] = True
            data_attr = attrs['⚡-data']
            if isinstance(data_attr, dict):
                data_attr = data_attr.get('key', 'unknown')
            node['_sanitize_key'] = str(data_attr)
        
        # Validate backend call endpoints
        if '⚡-call' in attrs:
            endpoint = attrs['⚡-call']
            if isinstance(endpoint, dict):
                endpoint = endpoint.get('endpoint', '')
            endpoint = str(endpoint)
            
            # Check for suspicious patterns
            if any(char in endpoint for char in ['..', '/', '\\']):
                self.warnings.append(ValidationIssue(
                    node,
                    f"Backend endpoint '{endpoint}' contains suspicious characters. "
                    f"Ensure this is intentional.",
                    severity='warning'
                ))
    
    def _validate_text(self, node: Dict[str, Any]):
        """Validate text node"""
        text = node.get('value', '')
        
        # Check for extremely long text (might be a paste error)
        if len(text) > 10000:
            self.warnings.append(ValidationIssue(
                node,
                f"Text content is extremely long ({len(text)} chars). "
                f"Consider moving to external content.",
                severity='warning'
            ))
    
    def _report_issues(self, category: str, issues: List[ValidationIssue]):
        """Pretty-print validation issues"""
        symbol = '❌' if category == 'ERRORS' else '⚠️ '
        
        print(f"\n{symbol} {category} in {self.filename}:\n")
        
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue.message}")
            if issue.line:
                print(f"   Line: {issue.line}")
            print()


# Test
if __name__ == '__main__':
    # Test with invalid code
    test_ast = {
        'type': 'Document',
        'children': [
            {
                'type': 'Element',
                'tag': 'div',
                'id': '🎨',  # INVALID - emoji
                'classes': ['valid-class'],
                'attributes': {},
                'children': [],
                'meta': {'line': 1}
            },
            {
                'type': 'Element',
                'tag': 'MyComponent',  # INVALID - should be my-component
                'id': 'test',
                'classes': [],
                'attributes': {
                    'animate': 'fade 1s',
                    'style': 'left: 100px'  # WARNING - bad for animation
                },
                'children': [],
                'meta': {'line': 5}
            }
        ]
    }
    
    validator = SemanticValidator(test_ast, 'test.htmlxify')
    result = validator.validate()
    
    print(f"\nValidation result: {'✅ PASSED' if result else '❌ FAILED'}")

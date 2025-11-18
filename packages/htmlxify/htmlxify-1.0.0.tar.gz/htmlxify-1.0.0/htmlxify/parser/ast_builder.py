"""
AST Builder - Converts Lark parse tree to custom Abstract Syntax Tree
PRODUCTION READY VERSION
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from lark import Lark, Transformer, Tree, Token

# Load grammar file
GRAMMAR_FILE = Path(__file__).parent / "grammar.lark"


class ASTTransformer(Transformer):
    """
    Transforms Lark parse tree to custom AST
    Matches grammar: start: element+
    """
    
    def start(self, children: list) -> Dict[str, Any]:
        """Root: start: element+"""
        elements = [c for c in children if c is not None]
        return {
            'type': 'Document',
            'children': elements,
            'meta': {}
        }
    
    def element(self, children: list) -> Dict[str, Any]:
        """
        element: tag_with_selectors attributes? body? | tag_with_selectors
        children[0] is always tag_with_selectors
        """
        if not children:
            return None
        
        # First child is always tag_with_selectors
        if isinstance(children[0], dict) and 'tag' in children[0]:
            tag_data = children[0]
        else:
            # Fallback for old parser state
            tag_data = {'tag': str(children[0]), 'classes': [], 'id': None}
        
        node = {
            'type': 'Element',
            'tag': tag_data['tag'],
            'classes': tag_data.get('classes', []),
            'id': tag_data.get('id'),
            'attributes': {},
            'children': []
        }
        
        # Process optional attributes and body
        for child in children[1:]:
            if child is None:
                continue
            
            if isinstance(child, dict):
                if child.get('_type') == 'attributes':
                    node['attributes'] = child['attrs']
                elif child.get('_type') == 'body':
                    node['children'] = child['children']
        
        return node
    
    def tag_with_selectors(self, children: list) -> Dict[str, Any]:
        """
        tag_with_selectors: WORD class_sel* id_sel?
        First child is WORD (tag), rest are selectors
        """
        tag = str(children[0])
        classes = []
        element_id = None
        
        # Process selectors
        for child in children[1:]:
            if isinstance(child, dict):
                if child.get('_type') == 'class':
                    classes.append(child['value'])
                elif child.get('_type') == 'id':
                    element_id = child['value']
        
        return {
            'tag': tag,
            'classes': classes,
            'id': element_id
        }
    
    def class_sel(self, children: list) -> Dict[str, Any]:
        """class_sel: "." WORD"""
        return {
            '_type': 'class',
            'value': str(children[0])
        }
    
    def id_sel(self, children: list) -> Dict[str, Any]:
        """id_sel: "#" WORD"""
        return {
            '_type': 'id',
            'value': str(children[0])
        }
    
    def attributes(self, children: list) -> Dict[str, Any]:
        """attributes: "(" attr_list ")" """
        attrs = children[0] if children else {}
        return {
            '_type': 'attributes',
            'attrs': attrs
        }
    
    def attr_list(self, children: list) -> Dict[str, Any]:
        """attr_list: attribute ("," attribute)*"""
        result = {}
        for attr in children:
            if isinstance(attr, dict):
                result.update(attr)
        return result
    
    def attribute(self, children: list) -> Dict[str, Any]:
        """
        attribute: attr_key ":" attr_value
        Lark filters out ":", so children = [key, value]
        """
        if len(children) >= 2:
            key = str(children[0])
            value = children[1]
            return {key: value}
        return {}
    
    def attr_key(self, children: list) -> str:
        """attr_key: SPECIAL_ATTR | WORD"""
        return str(children[0])
    
    def attr_value(self, children: list) -> Any:
        """attr_value: STRING | NUMBER | WORD"""
        return children[0]
    
    def body(self, children: list) -> Dict[str, Any]:
        """body: "{" body_content "}" """
        content = children[0] if children else []
        return {
            '_type': 'body',
            'children': content
        }
    
    def body_content(self, children: list) -> List[Any]:
        """body_content: body_item*"""
        return [c for c in children if c is not None]
    
    def body_element(self, children: list) -> Dict[str, Any]:
        """Alias for full_element inside body"""
        return children[0] if children else None
    
    def body_text(self, children: list) -> Dict[str, Any]:
        """Alias for text_content inside body"""
        return children[0] if children else None
    
    def full_element(self, children: list) -> Dict[str, Any]:
        """
        full_element: WORD class_sel* id_sel? attributes? body
        First child is WORD, rest are optional selectors/attributes/body
        """
        if not children:
            return None
        
        tag = str(children[0])
        classes = []
        element_id = None
        attributes = {}
        body_children = []
        
        # Process rest of children
        for child in children[1:]:
            if child is None:
                continue
            if isinstance(child, dict):
                if child.get('_type') == 'class':
                    classes.append(child['value'])
                elif child.get('_type') == 'id':
                    element_id = child['value']
                elif child.get('_type') == 'attributes':
                    attributes = child['attrs']
                elif child.get('_type') == 'body':
                    body_children = child['children']
        
        return {
            'type': 'Element',
            'tag': tag,
            'classes': classes,
            'id': element_id,
            'attributes': attributes,
            'children': body_children
        }
    
    def text_content(self, children: list) -> Dict[str, Any]:
        """text_content: text_token+"""
        text_parts = []
        for child in children:
            if isinstance(child, str):
                text_parts.append(child)
        
        text = ' '.join(text_parts).strip()
        if text:
            return {
                'type': 'Text',
                'value': text
            }
        return None
    
    def text_token(self, children: list) -> str:
        """text_token: TEXT_CHUNK | WORD"""
        return str(children[0]) if children else ''
    
    # ============================================================
    # TERMINAL HANDLERS
    # ============================================================
    
    def WORD(self, token: Token) -> str:
        return str(token)
    
    def TEXT_CHUNK(self, token: Token) -> str:
        return str(token)
    
    def STRING(self, token: Token) -> str:
        """Remove quotes from strings"""
        s = str(token)
        if (s.startswith('"') and s.endswith('"')) or \
           (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
        return s
    
    def NUMBER(self, token: Token) -> float:
        try:
            val = str(token)
            if '.' in val:
                return float(val)
            return int(val)
        except:
            return 0
    
    def SPECIAL_ATTR(self, token: Token) -> str:
        return str(token)




class ASTBuilder:
    """
    Main parser class - interfaces with Lark parser
    PRODUCTION READY
    """
    
    # Class-level parser cache for performance
    _parser_cache = None
    
    def __init__(self, source_code: str, filename: str):
        self.source = source_code
        self.filename = filename
        self.parser = None
        self._load_parser()
    
    def _load_parser(self):
        """Load and cache Lark parser"""
        # Use cached parser if available
        if ASTBuilder._parser_cache is not None:
            self.parser = ASTBuilder._parser_cache
            return
        
        try:
            with open(GRAMMAR_FILE, 'r', encoding='utf-8') as f:
                grammar = f.read()
            
            # Create parser with optimized settings
            self.parser = Lark(
                grammar,
                start='start',
                parser='earley',           # Handles ambiguity
                lexer='dynamic',           # Works with earley
                propagate_positions=True,  # Track line numbers
                maybe_placeholders=True,   # Allow None for optionals
                ambiguity='resolve'        # Auto-resolve ambiguity
            )
            
            # Cache for future instances
            ASTBuilder._parser_cache = self.parser
            
        except FileNotFoundError:
            print(f"❌ Error: Grammar file not found: {GRAMMAR_FILE}")
            raise
        except Exception as e:
            print(f"❌ Error loading grammar: {e}")
            raise
    
    def parse(self) -> Dict[str, Any]:
        """Parse source code into AST"""
        try:
            # Step 1: Parse with Lark
            tree = self.parser.parse(self.source)
            
            # Step 2: Transform to custom AST
            transformer = ASTTransformer()
            ast = transformer.transform(tree)
            
            return ast
            
        except Exception as e:
            self._handle_parse_error(e)
            raise
    
    def _handle_parse_error(self, error: Exception):
        """Pretty-print parser errors"""
        print(f"\n❌ Parse Error in {self.filename}:")
        print(f"   {str(error)}")
        
        # Try to extract line number
        error_str = str(error)
        if 'line' in error_str.lower():
            try:
                import re
                match = re.search(r'line (\d+)', error_str, re.IGNORECASE)
                if match:
                    line_num = int(match.group(1))
                    lines = self.source.split('\n')
                    if 0 <= line_num - 1 < len(lines):
                        print(f"\n   Line {line_num}: {lines[line_num - 1]}")
                        print(f"   {'':>{len(str(line_num)) + 7}}^")
            except:
                pass
        
        print()


# ============================================================
# TEST SUITE
# ============================================================

def test_parser():
    """Comprehensive test suite"""
    
    tests = [
        # Basic element
        ('div { Hello World }', 'Basic element with text'),
        
        # Classes
        ('div.container { Test }', 'Single class'),
        ('div.container.main { Test }', 'Multiple classes'),
        
        # ID
        ('div#app { Test }', 'ID selector'),
        
        # Classes + ID
        ('div.container.main#app { Test }', 'Classes and ID'),
        
        # Nested elements
        ('div { p { Nested } }', 'Nested element'),
        
        # Multiple children
        ('div { p { One } p { Two } }', 'Multiple children'),
        
        # Mixed content
        ('div { Some text p { Element } More text }', 'Mixed text and elements'),
        
        # Attributes
        ('button(onclick: "test") { Click }', 'Simple attribute'),
        ('button(id: "btn", class: "primary") { Click }', 'Multiple attributes'),
        
        # Special attributes
        ('button(⚡-call: "api") { Submit }', 'Backend call'),
        ('div(⚡-data: "userInfo") { }', 'Dynamic data'),
        
        # Complex example
        ('''div.container#main {
            header.navbar {
                h1 { My App }
            }
            section.content {
                p { Welcome to htmlxify }
                button(⚡-call: "login") { Login }
            }
        }''', 'Complex nested structure'),
    ]
    
    passed = 0
    failed = 0
    
    for code, description in tests:
        print(f"\n{'='*60}")
        print(f"Test: {description}")
        print(f"{'='*60}")
        print(f"Input:\n{code}\n")
        
        try:
            builder = ASTBuilder(code, 'test.htmlxify')
            ast = builder.parse()
            
            import json
            print("PASSED")
            print(json.dumps(ast, indent=2))
            passed += 1
            
        except Exception as e:
            print(f"FAILED: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    test_parser()


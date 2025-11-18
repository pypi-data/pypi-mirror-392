"""
Indentation Processor - Converts flat indented elements to nested tree
"""

from typing import Dict, Any, List


class IndentationProcessor:
    """
    Processes indentation to create hierarchical structure.
    
    Example:
    div {          # indent 0
      p {          # indent 1 -> child of div
        text       # indent 2 -> child of p
      }
      span {       # indent 1 -> sibling of p
        text
      }
    }
    """
    
    def process(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        """Convert flat list with indent info to nested tree"""
        if ast['type'] != 'Document':
            return ast
        
        elements = ast['children']
        if not elements:
            return ast
        
        # Build hierarchy using a stack
        root = {'type': 'Root', 'children': []}
        stack = [(root, -1)]  # (node, indent_level)
        
        for element in elements:
            if not isinstance(element, dict):
                continue
            
            indent = element.get('meta', {}).get('indent_level', 0)
            
            # Pop stack until we find the parent
            while len(stack) > 1 and stack[-1][1] >= indent:
                stack.pop()
            
            # Add element to current parent
            parent = stack[-1][0]
            parent['children'].append(element)
            
            # Push element onto stack
            stack.append((element, indent))
        
        return root


# Test
if __name__ == '__main__':
    from ast_builder import ASTBuilder
    
    code = '''
div {
  p { Outer }
  div {
    p { Nested }
  }
}
    '''
    
    builder = ASTBuilder(code, 'test.htmlxify')
    ast = builder.parse()
    
    processor = IndentationProcessor()
    nested_ast = processor.process(ast)
    
    import json
    print(json.dumps(nested_ast, indent=2))

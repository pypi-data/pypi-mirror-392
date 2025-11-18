"""
CSS Generator - Creates GPU-optimized CSS with default styles
"""

import tinycss2
import cssbeautifier
from typing import Dict, Any, List, Set


class CSSGenerator:
    """
    Generates CSS with:
    - Default semantic HTML styling
    - GPU-accelerated animations  
    - Class-based styling
    - Responsive design
    """
    
    # Default colors and spacing
    DEFAULT_STYLES = """
/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #333;
}

body {
  background-color: #fff;
  color: #333;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 0.5em;
}

h1 { font-size: 2.5rem; }
h2 { font-size: 2rem; }
h3 { font-size: 1.5rem; }
h4 { font-size: 1.25rem; }
h5 { font-size: 1.1rem; }
h6 { font-size: 1rem; }

p { margin-bottom: 1em; }
a { color: #0066cc; text-decoration: none; }
a:hover { text-decoration: underline; }

/* Lists */
ul, ol {
  margin-bottom: 1em;
  margin-left: 2em;
}

li { margin-bottom: 0.5em; }

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1em;
}

th, td {
  padding: 0.75em;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
  font-weight: 600;
}

tr:hover { background-color: #f9f9f9; }

/* Forms */
input, textarea, select {
  padding: 0.5em;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: inherit;
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

button {
  padding: 0.5em 1em;
  background-color: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #0052a3;
}

button:active {
  transform: scale(0.98);
}

/* Interactive Elements */
details {
  padding: 1em;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 1em;
}

summary {
  cursor: pointer;
  font-weight: 600;
  user-select: none;
}

summary:hover {
  color: #0066cc;
}

progress {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

progress::-webkit-progress-bar {
  background-color: #ddd;
}

progress::-webkit-progress-value {
  background-color: #0066cc;
}

meter {
  width: 100%;
  height: 8px;
}

/* Common Layout Classes */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1em;
}

.navbar {
  background-color: #f8f9fa;
  border-bottom: 1px solid #ddd;
  padding: 1em 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar a {
  color: #333;
  margin: 0 1em;
}

.navbar a:hover {
  color: #0066cc;
  text-decoration: none;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4em 1em;
  text-align: center;
}

.hero-title {
  font-size: 3rem;
  margin-bottom: 0.5em;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2em;
  opacity: 0.9;
}

.cta-button {
  background-color: white;
  color: #667eea;
  padding: 0.75em 2em;
  font-size: 1.1rem;
  margin-top: 1em;
}

.cta-button:hover {
  background-color: #f0f0f0;
}

/* Feature Grid */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2em;
  margin: 2em 0;
}

.feature-card {
  padding: 2em;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feature-badge {
  display: inline-block;
  padding: 0.25em 0.75em;
  background-color: #e8f4f8;
  color: #0066cc;
  border-radius: 20px;
  font-size: 0.9em;
  margin-top: 1em;
}

/* Statistics */
.statistics {
  padding: 3em 1em;
  background-color: #f5f5f5;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2em;
  max-width: 1200px;
  margin: 0 auto;
}

.stat-item {
  text-align: center;
  padding: 1em;
}

.stat-item h4 {
  font-size: 2em;
  color: #0066cc;
  margin-bottom: 0.5em;
}

/* Pricing Cards */
.pricing {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2em;
  padding: 2em 0;
}

.pricing-card {
  padding: 2em;
  border: 2px solid #ddd;
  border-radius: 8px;
  text-align: center;
  transition: all 0.2s;
}

.pricing-card.featured {
  border-color: #0066cc;
  background-color: #f0f7ff;
  transform: scale(1.05);
}

.pricing-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.badge {
  display: inline-block;
  background-color: #0066cc;
  color: white;
  padding: 0.25em 0.75em;
  border-radius: 20px;
  font-size: 0.85em;
  margin-bottom: 1em;
}

.price {
  font-size: 1.75em;
  color: #0066cc;
  font-weight: 600;
  margin: 1em 0;
}

.features-list {
  list-style: none;
  margin: 1em 0;
}

.features-list li {
  padding: 0.5em 0;
  border-bottom: 1px solid #ddd;
}

/* Comparison Table */
.comparison {
  width: 100%;
  border-collapse: collapse;
}

.comparison th,
.comparison td {
  padding: 1em;
  border: 1px solid #ddd;
}

.comparison th {
  background-color: #667eea;
  color: white;
  font-weight: 600;
}

.comparison tbody tr:nth-child(odd) {
  background-color: #f9f9f9;
}

.comparison tbody tr:hover {
  background-color: #f0f7ff;
}

/* Interactive Section */
.interactive-section {
  padding: 2em 1em;
}

.faq-content {
  padding: 1em 0;
}

/* Footer */
footer {
  background-color: #333;
  color: white;
  padding: 2em 1em;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2em;
  max-width: 1200px;
  margin: 0 auto;
  margin-bottom: 2em;
}

.footer-column h4 {
  color: white;
  margin-bottom: 1em;
}

.footer-column ul {
  list-style: none;
  margin: 0;
}

.footer-column li {
  margin-bottom: 0.5em;
}

.footer-column a {
  color: #aaa;
}

.footer-column a:hover {
  color: white;
}

.copyright {
  text-align: center;
  border-top: 1px solid #555;
  padding-top: 1em;
  margin-bottom: 0;
  color: #aaa;
}

/* Animations */
@keyframes fade {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes slide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(0); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* Responsive */
@media (max-width: 768px) {
  h1 { font-size: 1.75rem; }
  h2 { font-size: 1.5rem; }
  
  .hero-title { font-size: 1.75rem; }
  .feature-grid { grid-template-columns: 1fr; }
  .stats-container { grid-template-columns: 1fr; }
  .pricing { grid-template-columns: 1fr; }
  .pricing-card.featured { transform: scale(1); }
  .footer-content { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
  body { font-size: 14px; }
  .hero { padding: 2em 1em; }
  .hero-title { font-size: 1.25rem; }
  .footer-content { grid-template-columns: 1fr; }
}
"""
    
    def __init__(self, ast: Dict[str, Any]):
        self.ast = ast
        self.used_classes: Set[str] = set()
        self.styles: List[str] = []
        self.keyframes: List[str] = []
    
    def generate(self) -> str:
        """Generate CSS from AST"""
        # Start with default styles
        css = self.DEFAULT_STYLES
        
        # Extract any custom styles
        self._extract_styles(self.ast)
        
        # Add extracted custom styles
        if self.styles:
            css += '\n\n/* Custom Styles */\n'
            css += '\n\n'.join(self.styles)
        
        # Add keyframes
        if self.keyframes:
            css += '\n\n/* Custom Keyframes */\n'
            css += '\n\n'.join(self.keyframes)
        
        return css
    
    def _extract_styles(self, node: Any):
        """Recursively extract styles from AST"""
        if not isinstance(node, dict):
            return
        
        if node.get('type') == 'Element':
            self._process_element_styles(node)
        
        # Recurse
        for child in node.get('children', []):
            self._extract_styles(child)
    
    def _process_element_styles(self, node: Dict[str, Any]):
        """Process styles for single element"""
        attrs = node.get('attributes', {})
        
        # Track classes
        for cls in node.get('classes', []):
            self.used_classes.add(cls)
        
        # Inline style attribute
        if 'style' in attrs:
            selector = self._build_selector(node)
            style_rules = self._parse_style(attrs['style'])
            if style_rules:
                css_rule = f"{selector} {{\n  " + "\n  ".join(style_rules) + "\n}"
                self.styles.append(css_rule)
        
        # Animation (GPU-optimized)
        if 'animate' in attrs:
            selector = self._build_selector(node)
            anim_name, anim_rules = self._generate_animation(
                attrs['animate'], selector
            )
            rules = ['will-change: transform, opacity;', f'animation: {anim_name};']
            css_rule = f"{selector} {{\n  " + "\n  ".join(rules) + "\n}"
            self.styles.append(css_rule)
    
    def _build_selector(self, node: Dict[str, Any]) -> str:
        """Build CSS selector from node"""
        parts = [node.get('tag', 'div')]
        
        if node.get('id'):
            parts.append(f"#{node['id']}")
        
        if node.get('classes'):
            parts.extend(f".{cls}" for cls in node['classes'])
        
        return ''.join(parts)
    
    def _parse_style(self, style_obj: Any) -> List[str]:
        """Parse style object to CSS rules"""
        rules = []
        
        if isinstance(style_obj, dict):
            for key, value in style_obj.items():
                rules.append(f"{key}: {value};")
        elif isinstance(style_obj, str):
            rules.append(style_obj)
        
        return rules
    
    def _generate_animation(
        self, anim_def: Any, selector: str
    ) -> tuple:
        """Generate GPU-optimized animation"""
        if isinstance(anim_def, str):
            parts = anim_def.split()
        else:
            parts = [str(anim_def)]
        
        name = parts[0] if parts else 'anim'
        duration = parts[1] if len(parts) > 1 else '1s'
        timing = parts[2] if len(parts) > 2 else 'ease'
        
        return f"{name} {duration} {timing}", []


# Test
if __name__ == '__main__':
    test_ast = {
        'type': 'Document',
        'children': [
            {
                'type': 'Element',
                'tag': 'div',
                'id': 'hero',
                'classes': ['main'],
                'attributes': {
                    'style': {'bg': '#FF0000', 'pad': '20px'},
                    'animate': 'fade 2s ease-in'
                },
                'children': []
            }
        ]
    }
    
    gen = CSSGenerator(test_ast)
    css = gen.generate()
    
    print("Generated CSS:")
    print(css)

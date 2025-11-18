"""
JS Generator - Secure JavaScript with XSS prevention
"""

from typing import Dict, Any, List, Set


class JSGenerator:
    """
    Generates JavaScript for:
    - API call handlers
    - Dynamic data binding
    - Animation cleanup
    """
    
    def __init__(self, ast: Dict[str, Any]):
        self.ast = ast
        self.scripts: List[str] = []
        self.api_calls: Set[str] = set()
        self.data_bindings: Set[str] = set()
    
    def generate(self) -> str:
        """Generate all JavaScript"""
        self._scan_ast(self.ast)
        self._generate_api_handlers()
        self._generate_data_bindings()
        self._generate_animation_cleanup()
        
        if not self.scripts:
            return "// No dynamic content"
        
        return '\n\n'.join(self.scripts)
    
    def _scan_ast(self, node: Any):
        """Scan AST for special attributes"""
        if not isinstance(node, dict):
            return
        
        if node.get('type') == 'Element':
            attrs = node.get('attributes', {})
            
            # Collect API calls
            if '⚡-call' in attrs:
                call_val = attrs['⚡-call']
                endpoint = call_val
                if isinstance(call_val, dict):
                    endpoint = call_val.get('endpoint', '')
                if endpoint:
                    self.api_calls.add(str(endpoint))
            
            # Collect data bindings
            if '⚡-data' in attrs:
                data_val = attrs['⚡-data']
                data_key = data_val
                if isinstance(data_val, dict):
                    data_key = data_val.get('key', '')
                if data_key:
                    self.data_bindings.add(str(data_key))
        
        # Recurse
        for child in node.get('children', []):
            self._scan_ast(child)
    
    def _generate_api_handlers(self):
        """Generate API handler functions with configurable backend URL"""
        if not self.api_calls:
            return
        
        code = """// Backend API Configuration
// Users can set the API URL in 3 ways (no compiler changes needed):
//
// 1. In your HTML file, add a meta tag:
//    <meta name="api-url" content="https://api.yourdomain.com">
//
// 2. In your HTML file or script, set window variable:
//    <script>window.API_BASE_URL = 'https://api.yourdomain.com';</script>
//
// 3. Create a config.js file and include it before this script:
//    <script src="config.js"></script>
//    window.API_BASE_URL = 'https://api.yourdomain.com';
//
// Priority order (first one found is used):
//   1. window.API_BASE_URL (highest priority)
//   2. meta[name="api-url"] content attribute  
//   3. /api (relative URL - same domain as frontend)
//   4. http://localhost:5000/api (local development default)

const API_BASE_URL = window.API_BASE_URL 
  || (function() {
    const meta = document.querySelector('meta[name="api-url"]');
    if (meta) return meta.getAttribute('content');
    
    // Use relative URL if not on localhost
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      return '/api';
    }
    
    // Default to localhost for development
    return 'http://localhost:5000/api';
  })();

console.log('API Configuration - API_BASE_URL:', API_BASE_URL);

// API Handlers (calls backend server)
const apiHandlers = {
"""
        
        for endpoint in sorted(self.api_calls):
            code += f"""  '{endpoint}': async function(element) {{
    try {{
      const plan = element.getAttribute('data-plan');
      const url = plan 
        ? API_BASE_URL + '/{endpoint}/' + plan 
        : API_BASE_URL + '/{endpoint}';
      
      const response = await fetch(url, {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
        }},
        body: JSON.stringify({{ timestamp: new Date().toISOString() }})
      }});
      
      if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
      
      const data = await response.json();
      console.log('{endpoint} response:', data);
      
      // Update element with response data
      const parent = element.closest('[data-container]') || element.parentElement;
      if (parent) {{
        const content = document.createElement('div');
        content.className = 'api-response';
        content.textContent = data.message || JSON.stringify(data);
        parent.appendChild(content);
      }}
    }} catch (error) {{
      console.error('{endpoint} error:', error);
      element.textContent = 'Error: ' + error.message;
    }}
  }},
"""
        
        code += """};\n
// Auto-trigger API handlers on page load
document.addEventListener('DOMContentLoaded', function() {
  console.log('API_BASE_URL:', API_BASE_URL);
  
  document.querySelectorAll('[data-api-call]').forEach(element => {
    const endpoint = element.getAttribute('data-api-call');
    if (apiHandlers[endpoint]) {
      console.log('Calling API:', endpoint);
      apiHandlers[endpoint](element);
    } else {
      console.warn('No handler for endpoint:', endpoint);
    }
  });
});"""
        
        self.scripts.append(code)
    
    def _generate_data_bindings(self):
        """Generate data binding code"""
        if not self.data_bindings:
            return
        
        code = """// Data Bindings
const dataBindings = {
"""
        
        for binding in sorted(self.data_bindings):
            code += f"""  '{binding}': null,
"""
        
        code += """};\n
function updateBinding(key, value) {
  dataBindings[key] = value;
  document.querySelectorAll(`[data-dynamic="${key}"]`).forEach(element => {
    element.textContent = value;
    element.dispatchEvent(new CustomEvent('dataUpdate', { detail: { key, value } }));
  });
}\n
// Example: updateBinding('myData', 'new value');
"""
        
        self.scripts.append(code)
    
    def _generate_animation_cleanup(self):
        """Generate animation cleanup code"""
        code = """// Animation Utilities
const animationUtils = {
  // Remove animation class after animation completes
  removeAnimationClass: function(element, className) {
    element.addEventListener('animationend', function() {
      element.classList.remove(className);
    }, { once: true });
  },
  
  // Prefetch images for animations
  prefetchImages: function(urls) {
    urls.forEach(url => {
      const img = new Image();
      img.src = url;
    });
  },
  
  // Request animation frame for smooth animations
  smoothScroll: function(element, duration = 300) {
    const start = window.scrollY;
    const target = element.offsetTop;
    const distance = target - start;
    const startTime = performance.now();
    
    function easeInOutQuad(t) {
      return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }
    
    function scroll(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = easeInOutQuad(progress);
      
      window.scrollTo(0, start + distance * ease);
      
      if (progress < 1) {
        requestAnimationFrame(scroll);
      }
    }
    
    requestAnimationFrame(scroll);
  }
};"""
        
        self.scripts.append(code)


# Test
if __name__ == '__main__':
    test_ast = {
        'type': 'Document',
        'children': [
            {
                'type': 'Element',
                'tag': 'div',
                'id': 'data',
                'classes': [],
                'attributes': {
                    '⚡-call': {'type': 'backend_call', 'endpoint': 'getData'},
                    '⚡-data': {'type': 'dynamic_data', 'key': 'user'}
                },
                'children': []
            }
        ]
    }
    
    gen = JSGenerator(test_ast)
    js = gen.generate()
    
    print("Generated JavaScript:")
    print(js)

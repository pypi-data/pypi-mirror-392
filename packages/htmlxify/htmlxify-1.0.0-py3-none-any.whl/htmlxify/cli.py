#!/usr/bin/env python3
"""
htmlxify Compiler - Command Line Interface
Usage: htmlxify input.htmlxify [output-dir]
"""

import sys
import argparse
from pathlib import Path

from htmlxify.parser.ast_builder import ASTBuilder
from htmlxify.parser.indent_processor import IndentationProcessor
from htmlxify.validator.semantic import SemanticValidator
from htmlxify.generators.html_gen import HTMLGenerator
from htmlxify.generators.css_gen import CSSGenerator
from htmlxify.generators.js_gen import JSGenerator


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='htmlxify Compiler',
        epilog='Example: htmlxify index.htmlxify dist/'
    )
    
    parser.add_argument(
        'input',
        help='Input .htmlxify file to compile'
    )
    
    parser.add_argument(
        'output',
        nargs='?',
        default='dist',
        help='Output directory (default: dist)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='htmlxify Compiler 1.0.0'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File '{args.input}' not found")
        sys.exit(1)
    
    if input_path.suffix not in ['.htmlxify']:
        print(f"⚠️  Warning: File extension should be .htmlxify")
    
    # Read source
    try:
        source = input_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: reading file: {e}")
        sys.exit(1)
    
    print(f"\nCompiling {input_path.name}...\n")
    
    try:
        # Step 1: Parse
        if args.verbose:
            print("Step 1/6: Parsing...")
        
        ast_builder = ASTBuilder(source, input_path.name)
        ast = ast_builder.parse()
        print("OK - Parsing complete")
        
        # Step 2: Process indentation
        if args.verbose:
            print("Step 2/6: Processing indentation...")
        
        indent_processor = IndentationProcessor()
        ast = indent_processor.process(ast)
        print("OK - Indentation processed")
        
        # Step 3: Validate
        if args.verbose:
            print("Step 3/6: Validating...")
        
        validator = SemanticValidator(ast, input_path.name)
        if not validator.validate():
            sys.exit(1)
        print("OK - Validation complete")
        
        # Step 4: Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Step 5: Generate HTML
        if args.verbose:
            print("Step 4/6: Generating HTML...")
        
        html_gen = HTMLGenerator(ast, input_path.name)
        html, source_map = html_gen.generate()
        
        html_path = output_dir / input_path.name.replace('.htmlxify', '.html')
        html_path.write_text(html, encoding='utf-8')
        
        # Write source map
        source_map_path = output_dir / (input_path.name.replace('.htmlxify', '.html') + '.map')
        source_map_path.write_text(source_map, encoding='utf-8')
        
        print(f"OK - Generated {html_path}")
        
        # Step 6: Generate CSS
        if args.verbose:
            print("Step 5/6: Generating CSS...")
        
        css_gen = CSSGenerator(ast)
        css = css_gen.generate()
        
        css_path = output_dir / input_path.name.replace('.htmlxify', '.css')
        css_path.write_text(css, encoding='utf-8')
        print(f"OK - Generated {css_path}")
        
        # Step 7: Generate JavaScript
        if args.verbose:
            print("Step 6/6: Generating JavaScript...")
        
        js_gen = JSGenerator(ast)
        js = js_gen.generate()
        
        js_path = output_dir / input_path.name.replace('.htmlxify', '.js')
        js_path.write_text(js, encoding='utf-8')
        print(f"OK - Generated {js_path}")
        
        print("\nCompilation successful!\n")
        
    except KeyboardInterrupt:
        print("\n\nCompilation cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\nCompilation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

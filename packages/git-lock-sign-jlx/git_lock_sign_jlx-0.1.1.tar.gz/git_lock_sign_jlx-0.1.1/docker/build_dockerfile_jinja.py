#!/usr/bin/env python3
"""
Build Dockerfile from Jinja2 template using base.yaml and values.yaml
"""
import yaml
import argparse
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

def dockerfileBlock(script_content, instruction='RUN'):
    """
    Jinja2 filter to format script content as a Docker RUN block.
    This mimics the behavior expected by the templates.
    """
    if not script_content or not script_content.strip():
        return ""
    
    lines = script_content.strip().split('\n')
    if len(lines) == 1:
        return f"{instruction} {lines[0]}"
    else:
        # Multi-line script - format with proper line continuations
        result = f"{instruction} {lines[0]}"
        for line in lines[1:]:
            # Preserve existing line continuations, add indentation
            result += f"\n    {line}"
        return result

def main():
    parser = argparse.ArgumentParser(description='Build Dockerfile from Jinja2 template')
    parser.add_argument('--template', required=True, help='Jinja2 template file path')
    parser.add_argument('--values', required=True, help='Values YAML file path')
    parser.add_argument('--base', required=True, help='Base YAML file path')
    parser.add_argument('--output', required=True, help='Output Dockerfile path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate input files exist
    template_path = Path(args.template)
    values_path = Path(args.values)
    base_path = Path(args.base)
    
    if not template_path.exists():
        print(f"Error: Template file not found: {template_path}")
        sys.exit(1)
    if not values_path.exists():
        print(f"Error: Values file not found: {values_path}")
        sys.exit(1)
    if not base_path.exists():
        print(f"Error: Base file not found: {base_path}")
        sys.exit(1)
    
    # Load configuration files
    try:
        with open(values_path, 'r') as f:
            values = yaml.safe_load(f)
        if args.verbose:
            print(f"✅ Loaded values from {values_path}")
    except Exception as e:
        print(f"Error loading values file: {e}")
        sys.exit(1)
    
    try:
        with open(base_path, 'r') as f:
            base_config = yaml.safe_load(f)
        if args.verbose:
            print(f"✅ Loaded base config from {base_path}")
    except Exception as e:
        print(f"Error loading base file: {e}")
        sys.exit(1)
    
    # Set up Jinja2 environment
    template_dir = template_path.parent
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Add custom filter for Docker blocks
    env.filters['dockerfileBlock'] = dockerfileBlock
    
    # Load the template
    try:
        template = env.get_template(template_path.name)
        if args.verbose:
            print(f"✅ Loaded template from {template_path}")
    except Exception as e:
        print(f"Error loading template: {e}")
        sys.exit(1)
    
    # Prepare template context
    context = {
        'base': base_config.get('base', 'jupyter/base-notebook'),
        'hash': 'generated',  # Could be git hash or timestamp
    }
    
    # Process packages into the format expected by templates
    processed_packages = {}
    
    # Process apt packages
    if 'apt' in values and values['apt']:
        processed_apt = []
        for item in values['apt']:
            if isinstance(item, str):
                processed_apt.append({'key': item})
            elif isinstance(item, dict):
                for key in item.keys():
                    processed_apt.append({'key': key})
        processed_packages['apt'] = processed_apt
        if args.verbose:
            print(f"📦 Processed {len(processed_apt)} apt packages")
    
    # Process conda packages
    if 'conda' in values and values['conda']:
        processed_conda = []
        for item in values['conda']:
            if isinstance(item, str):
                processed_conda.append({'key': item})
            elif isinstance(item, dict):
                for key, value in item.items():
                    processed_conda.append({'key': key, 'value': value})
        processed_packages['conda'] = processed_conda
        if args.verbose:
            print(f"📦 Processed {len(processed_conda)} conda packages")
    
    # Process pip packages
    if 'pip' in values and values['pip']:
        processed_pip = []
        for item in values['pip']:
            if isinstance(item, str):
                processed_pip.append({'key': item})
            elif isinstance(item, dict):
                for key, value in item.items():
                    processed_pip.append({'key': key, 'value': value})
        processed_packages['pip'] = processed_pip
        if args.verbose:
            print(f"📦 Processed {len(processed_pip)} pip packages")
    
    # Process environment variables
    if 'env' in values and values['env']:
        processed_env = []
        for item in values['env']:
            if isinstance(item, dict):
                for key, value in item.items():
                    processed_env.append({'key': key, 'value': value})
        processed_packages['env'] = processed_env
        if args.verbose:
            print(f"🔧 Processed {len(processed_env)} environment variables")
    
    # Add processed packages to context
    context.update(processed_packages)
    
    # Add remaining values to context
    for key, value in values.items():
        if key not in processed_packages:
            context[key] = value
    
    # Process add_files to create temporary files if needed
    temp_files_created = []
    add_files_processed = []
    
    if 'addfiles' in values:
        for file_item in values['addfiles']:
            if isinstance(file_item, dict):
                for name, config in file_item.items():
                    if config.get('source', '').strip() and config['source'] != '.':
                        # Create temporary file for content
                        temp_file_name = f"temp_{name}"
                        temp_file_path = Path(args.output).parent / temp_file_name
                        
                        try:
                            with open(temp_file_path, 'w') as tf:
                                tf.write(config['source'])
                            temp_files_created.append(temp_file_path)
                            
                            # Update the config to point to temp file
                            processed_config = config.copy()
                            # For Docker build context, use relative path
                            docker_temp_path = f"docker/jupyterlab/{temp_file_name}"
                            
                            add_files_processed.append({
                                'key': docker_temp_path,
                                'value': config['destination'],
                                'permissions': config.get('permissions'),
                                'name': name
                            })
                            
                            if args.verbose:
                                print(f"📝 Created temp file: {temp_file_path}")
                                
                        except Exception as e:
                            print(f"Error creating temp file {temp_file_path}: {e}")
                            sys.exit(1)
                    else:
                        # Handle source code copy (source = '.')
                        add_files_processed.append({
                            'key': '.',
                            'value': config['destination'],
                            'permissions': config.get('permissions'),
                            'name': name
                        })
    
    # Update context with processed files
    context['add_files'] = add_files_processed
    
    # Process scripts to ensure they're in the right format
    scripts_processed = []
    if 'scripts' in values:
        for script_item in values['scripts']:
            if isinstance(script_item, dict):
                for name, content in script_item.items():
                    scripts_processed.append(content.strip())
            elif isinstance(script_item, str):
                scripts_processed.append(script_item.strip())
    
    context['scripts'] = scripts_processed
    
    # Render the template
    try:
        rendered = template.render(**context)
        if args.verbose:
            print(f"✅ Template rendered successfully")
    except Exception as e:
        print(f"Error rendering template: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Write the output
    output_path = Path(args.output)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(rendered)
        if args.verbose:
            print(f"✅ Wrote Dockerfile to {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)
    
    # Summary
    print(f"🚀 Successfully generated {output_path}")
    if temp_files_created:
        print(f"📁 Created {len(temp_files_created)} temporary files:")
        for temp_file in temp_files_created:
            print(f"   - {temp_file.name}")
        print("   (These will be cleaned up after Docker build)")
    
    # Print some useful info
    if args.verbose:
        print(f"\n📊 Template context summary:")
        print(f"   - Base image: {context.get('base')}")
        print(f"   - Apt packages: {len(context.get('apt', []))}")
        print(f"   - Conda packages: {len(context.get('conda', []))}")
        print(f"   - Pip packages: {len(context.get('pip', []))}")
        print(f"   - Scripts: {len(context.get('scripts', []))}")
        print(f"   - Files: {len(context.get('add_files', []))}")
        print(f"   - Environment vars: {len(context.get('env', []))}")

if __name__ == '__main__':
    main()

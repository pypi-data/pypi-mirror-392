"""Multi-format processor for detecting and replacing secrets in various file formats."""

from typing import Dict, Any, List, Tuple
from mask_env.core import _is_secret_value, _generate_placeholder
from mask_env.formats import parse_file, format_file, detect_format


def process_file(input_path: str, output_path: str = None) -> int:
    """Process any supported file format and create safe example.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file (default: input_path + '.example')
        
    Returns:
        Number of secrets replaced
    """
    format_type = detect_format(input_path)
    
    if format_type == 'env':
        # Use existing .env processor
        from mask_env.core import create_safe_example
        return create_safe_example(input_path, output_path)
    elif format_type == 'key':
        # Key/certificate files - entire file is secret
        return _process_key_file(input_path, output_path)
    else:
        # Structured formats (JSON, YAML, INI, TOML, properties)
        return _process_structured_file(input_path, output_path, format_type)


def _process_key_file(input_path: str, output_path: str = None) -> int:
    """Process key/certificate file (entire file is secret)."""
    if output_path is None:
        output_path = input_path + '.example'
    
    # Read original
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Write placeholder
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# WARNING: Do not add real secrets to this file!\n")
        f.write("# This is an example file with placeholders.\n")
        f.write("# Copy this file and fill in your actual key/certificate.\n")
        f.write("\n")
        f.write("# YOUR_PRIVATE_KEY_OR_CERTIFICATE_HERE\n")
        f.write("# Replace this placeholder with your actual key/certificate content.\n")
    
    return 1  # Entire file counted as one secret


def _process_structured_file(input_path: str, output_path: str = None, format_type: str = None) -> int:
    """Process structured file formats (JSON, YAML, INI, TOML, properties)."""
    if output_path is None:
        output_path = input_path + '.example'
    
    if format_type is None:
        format_type = detect_format(input_path)
    
    # Parse file
    parsed_format, data = parse_file(input_path, format_type)
    
    # Check for errors
    if isinstance(data, dict) and '_error' in data:
        raise ValueError(f"Cannot process {format_type} file: {data['_error']}")
    
    # Process data structure
    secrets_replaced = _process_data_structure(data, format_type)
    
    # Format and write output
    output_content = format_file(data, format_type, input_path)
    
    # Add header comment for structured formats
    header = _get_format_header(format_type)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(output_content)
    
    return secrets_replaced


def _process_data_structure(data: Any, format_type: str, path: str = '') -> int:
    """Recursively process data structure to find and replace secrets.
    
    Args:
        data: Data structure (dict, list, or primitive)
        format_type: Format type for context
        path: Current path in structure (for nested keys)
        
    Returns:
        Number of secrets replaced
    """
    secrets_replaced = 0
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, (dict, list)):
                # Recursively process nested structures
                secrets_replaced += _process_data_structure(value, format_type, current_path)
            elif isinstance(value, str):
                # Check if string value is a secret
                if _is_secret_value(value):
                    # Replace with placeholder - use full path for nested keys
                    placeholder = _generate_placeholder(current_path.replace('.', '_'))
                    data[key] = placeholder
                    secrets_replaced += 1
            # Numbers, booleans, None are not secrets
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            
            if isinstance(item, (dict, list)):
                # Recursively process nested structures
                secrets_replaced += _process_data_structure(item, format_type, current_path)
            elif isinstance(item, str):
                # Check if string value is a secret
                if _is_secret_value(item):
                    # Replace with placeholder
                    base_key = path.split('.')[-1] if path else "item"
                    placeholder = _generate_placeholder(f"{base_key}_{i}")
                    data[i] = placeholder
                    secrets_replaced += 1
    
    return secrets_replaced


def _get_format_header(format_type: str) -> str:
    """Get header comment for different formats."""
    if format_type == 'json':
        return "// WARNING: Do not add real secrets to this file!\n// This is an example file with placeholders.\n// Copy this file and fill in your actual values.\n\n"
    elif format_type in ('yaml', 'yml'):
        return "# WARNING: Do not add real secrets to this file!\n# This is an example file with placeholders.\n# Copy this file and fill in your actual values.\n\n"
    elif format_type == 'toml':
        return "# WARNING: Do not add real secrets to this file!\n# This is an example file with placeholders.\n# Copy this file and fill in your actual values.\n\n"
    elif format_type in ('ini', 'properties'):
        return "# WARNING: Do not add real secrets to this file!\n# This is an example file with placeholders.\n# Copy this file and fill in your actual values.\n\n"
    else:
        return ""


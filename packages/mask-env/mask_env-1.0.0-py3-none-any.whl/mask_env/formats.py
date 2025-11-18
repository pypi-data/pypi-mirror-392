
"""Format detection and parsing for different secret file formats."""

import json
import configparser
import os
from typing import Tuple, Dict, Any, Optional, List


def detect_format(file_path: str) -> str:
    """Detect file format based on extension and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Format name: 'env', 'json', 'yaml', 'ini', 'properties', 'toml', 'key'
    """
    ext = os.path.splitext(file_path)[1].lower()
    basename = os.path.basename(file_path).lower()
    
    # Key/certificate files
    if ext in ('.pem', '.key', '.crt', '.p12', '.pfx'):
        return 'key'
    
    # .env files
    if ext == '.env' or basename.startswith('.env'):
        return 'env'
    
    # JSON files
    if ext == '.json':
        return 'json'
    
    # YAML files
    if ext in ('.yaml', '.yml'):
        return 'yaml'
    
    # TOML files
    if ext == '.toml':
        return 'toml'
    
    # Properties files
    if ext == '.properties':
        return 'properties'
    
    # INI/CFG/CONF files
    if ext in ('.ini', '.cfg', '.conf'):
        return 'ini'
    
    # Default to env for unknown
    return 'env'


def parse_file(file_path: str, format_type: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """Parse a file and return format type and parsed content.
    
    Args:
        file_path: Path to the file
        format_type: Optional format type (auto-detected if None)
        
    Returns:
        Tuple of (format_type, parsed_data)
        
    Raises:
        ValueError: If format is not supported or file cannot be parsed
    """
    if format_type is None:
        format_type = detect_format(file_path)
    
    if format_type == 'env':
        return ('env', {'lines': _read_env_file(file_path)})
    elif format_type == 'json':
        return ('json', _parse_json_file(file_path))
    elif format_type == 'ini':
        return ('ini', _parse_ini_file(file_path))
    elif format_type == 'properties':
        return ('properties', _parse_properties_file(file_path))
    elif format_type == 'yaml':
        return ('yaml', _parse_yaml_file(file_path))
    elif format_type == 'toml':
        return ('toml', _parse_toml_file(file_path))
    elif format_type == 'key':
        return ('key', {'content': _read_key_file(file_path)})
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def _read_env_file(file_path: str) -> List[str]:
    """Read .env file as lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()


def _parse_json_file(file_path: str) -> Dict[str, Any]:
    """Parse JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _parse_ini_file(file_path: str) -> Dict[str, Any]:
    """Parse INI/CFG/CONF file."""
    parser = configparser.ConfigParser()
    parser.read(file_path, encoding='utf-8')
    
    # Convert to dict structure
    result = {}
    for section in parser.sections():
        result[section] = dict(parser.items(section))
    
    # Handle DEFAULT section if present
    if parser.defaults():
        result['DEFAULT'] = dict(parser.defaults())
    
    return result


def _parse_properties_file(file_path: str) -> Dict[str, Any]:
    """Parse .properties file (Java-style key=value)."""
    result = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Skip comments and blank lines
            if not line or line.startswith('#'):
                continue
            
            # Handle key=value
            if '=' in line:
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip()
            # Handle key:value (alternative format)
            elif ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
    
    return result


def _parse_yaml_file(file_path: str) -> Dict[str, Any]:
    """Parse YAML file.
    
    Note: Requires 'pyyaml' package. Returns error dict if not available.
    """
    try:
        import yaml
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {'_error': 'YAML support requires pyyaml package. Install with: pip install pyyaml'}
    except Exception as e:
        return {'_error': f'Failed to parse YAML: {e}'}


def _parse_toml_file(file_path: str) -> Dict[str, Any]:
    """Parse TOML file.
    
    Note: Requires 'toml' or 'tomli' package. Returns error dict if not available.
    """
    try:
        # Try tomli first (Python 3.11+ stdlib, but also available as package)
        try:
            import tomli
            with open(file_path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            # Fall back to toml package
            import toml
            with open(file_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
    except ImportError:
        return {'_error': 'TOML support requires tomli or toml package. Install with: pip install tomli'}
    except Exception as e:
        return {'_error': f'Failed to parse TOML: {e}'}


def _read_key_file(file_path: str) -> str:
    """Read key/certificate file (entire file is secret)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def format_file(data: Dict[str, Any], format_type: str, original_path: Optional[str] = None) -> str:
    """Format data back to file content.
    
    Args:
        data: Parsed data structure
        format_type: Format type
        original_path: Original file path (for preserving formatting)
        
    Returns:
        Formatted file content as string
    """
    if format_type == 'env':
        return ''.join(data.get('lines', []))
    elif format_type == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    elif format_type == 'ini':
        return _format_ini(data)
    elif format_type == 'properties':
        return _format_properties(data)
    elif format_type == 'yaml':
        return _format_yaml(data)
    elif format_type == 'toml':
        return _format_toml(data)
    elif format_type == 'key':
        return data.get('content', '')
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def _format_ini(data: Dict[str, Any]) -> str:
    """Format data as INI file."""
    parser = configparser.ConfigParser()
    
    for section, items in data.items():
        if section == 'DEFAULT':
            parser.read_dict({'DEFAULT': items})
        else:
            parser.add_section(section)
            for key, value in items.items():
                parser.set(section, key, str(value))
    
    # Write to string
    import io
    output = io.StringIO()
    parser.write(output)
    return output.getvalue()


def _format_properties(data: Dict[str, Any]) -> str:
    """Format data as .properties file."""
    lines = []
    for key, value in data.items():
        lines.append(f"{key}={value}\n")
    return ''.join(lines)


def _format_yaml(data: Dict[str, Any]) -> str:
    """Format data as YAML file."""
    try:
        import yaml
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except ImportError:
        return "# YAML support requires pyyaml package\n"


def _format_toml(data: Dict[str, Any]) -> str:
    """Format data as TOML file."""
    try:
        try:
            import tomli_w
            return tomli_w.dumps(data)
        except ImportError:
            import toml
            return toml.dumps(data)
    except ImportError:
        return "# TOML support requires tomli or toml package\n"


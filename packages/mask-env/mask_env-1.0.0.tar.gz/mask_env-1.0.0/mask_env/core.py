"""Core logic for detecting and replacing secrets in .env files.

This module provides the core secret detection and .env file processing.
For multi-format support, see mask_env.processor module.
"""


def _is_secret_value(value):
    """Check if a value looks like a secret using lightweight heuristics.
    
    No hardcoded patterns - uses general characteristics:
    - Length (secrets are often long)
    - Character distribution (random-looking)
    - Excludes obvious non-secrets (URLs, emails, paths)
    
    Optimized for thousands of variables - no expensive operations.
    """
    if not value:
        return False
    
    # Remove surrounding quotes if present (fast check)
    value_stripped = value.strip()
    if len(value_stripped) >= 2:
        if (value_stripped[0] == '"' and value_stripped[-1] == '"') or \
           (value_stripped[0] == "'" and value_stripped[-1] == "'"):
            value_stripped = value_stripped[1:-1].strip()
    
    if not value_stripped:
        return False
    
    value_len = len(value_stripped)
    
    # Quick exclusion: very short values are unlikely to be secrets
    if value_len < 12:
        return False
    
    # Check for connection strings with embedded credentials
    # Pattern: scheme://user:password@host or scheme://:password@host
    # Use tuple for fast membership testing and early exit optimization
    connection_schemes = ('postgresql://', 'postgres://', 'mysql://', 'mongodb://', 
                         'redis://', 'amqp://', 'rabbitmq://', 'cassandra://',
                         'neo4j://', 'memcached://', 'couchdb://', 'influxdb://')
    
    is_connection_string = False
    password_part = None
    
    # Quick check: connection strings must contain :// and @
    if '://' in value_stripped and '@' in value_stripped:
        # Find scheme match (optimized: check most common first)
        for scheme in connection_schemes:
            if value_stripped.startswith(scheme):
                is_connection_string = True
                # Extract the part after scheme://
                after_scheme = value_stripped[len(scheme):]
                
                # Check for user:password@ or :password@ pattern
                if '@' in after_scheme:
                    # Split at @ to get credentials and host (max 1 split for performance)
                    creds_and_host = after_scheme.split('@', 1)
                    if len(creds_and_host) == 2:
                        creds = creds_and_host[0]
                        # Check for password (either user:password or :password)
                        if ':' in creds:
                            # Extract password part
                            if creds.startswith(':'):
                                # Format: :password@host
                                password_part = creds[1:]
                            else:
                                # Format: user:password@host (split only once)
                                password_parts = creds.split(':', 1)
                                if len(password_parts) == 2:
                                    password_part = password_parts[1]
                        # If no ':' in creds, it's just username, no password
                break
    
    # If it's a connection string with a password, check the password part
    if is_connection_string and password_part:
        # Connection strings with embedded passwords are always suspicious
        # Even short passwords in connection strings should be treated as secrets
        # (connection strings themselves are sensitive)
        password_lower = password_part.lower()
        obvious_placeholders = ('pass', 'pwd', 'user', 'admin', 'test', 'demo', 'none', '')
        
        if len(password_part) >= 8:
            # Password is 8+ chars, treat as secret (even if it's a common word)
            return True
        elif len(password_part) >= 4:
            # Password is 4-7 chars, treat as secret unless it's an obvious placeholder
            if password_lower not in obvious_placeholders:
                return True
        elif len(password_part) >= 3:
            # Very short passwords (3 chars) - still suspicious in connection strings
            # Only exclude if it's clearly a placeholder
            if password_lower not in ('pwd', 'pwd', ''):
                return True
    
    # Quick exclusion: obvious non-secrets (but not connection strings)
    # URLs (but not connection strings)
    if not is_connection_string and value_stripped.startswith(('http://', 'https://', 'ftp://')):
        return False
    
    # Email addresses (but not connection strings)
    if not is_connection_string and '@' in value_stripped and '.' in value_stripped:
        # Simple heuristic: if it looks like an email
        parts = value_stripped.split('@')
        if len(parts) == 2 and '.' in parts[1]:
            return False
    
    # File paths (Unix/Windows)
    if value_stripped.startswith(('/', '\\', './', '.\\')):
        return False
    
    # Check for private key markers (common pattern, worth checking)
    value_upper = value_stripped.upper()
    if 'BEGIN' in value_upper and 'PRIVATE' in value_upper:
        return True
    
    # Single-pass character analysis for efficiency
    alnum_count = 0
    digit_count = 0
    upper_count = 0
    lower_count = 0
    separator_count = 0
    space_count = 0
    
    for char in value_stripped:
        if char.isalnum():
            alnum_count += 1
            if char.isdigit():
                digit_count += 1
            elif char.isupper():
                upper_count += 1
            elif char.islower():
                lower_count += 1
        elif char in ('-', '_', '.', '+', '/', '='):
            separator_count += 1
        elif char.isspace():
            space_count += 1
    
    # Exclude values with spaces (likely not secrets)
    if space_count > 0:
        return False
    
    alnum_ratio = alnum_count / value_len
    separator_ratio = separator_count / value_len
    
    # Secrets typically have:
    # - High alphanumeric ratio (>80%)
    # - Mix of upper/lower/digits (indicates randomness)
    # - Low separator ratio (<25%) unless it's a structured format
    # - Length 12+ for shorter secrets, 20+ for longer ones
    
    if alnum_ratio > 0.80:
        has_mixed_case = upper_count > 0 and lower_count > 0
        has_digits = digit_count > 0
        
        # For longer values (20+), be more lenient
        if value_len >= 20:
            if separator_ratio < 0.3:
                # Long values with high alnum ratio are likely secrets
                # Especially if they have mixed case, digits, or high alnum ratio
                if has_mixed_case or has_digits or alnum_ratio > 0.85:
                    return True
        # For medium values (16-19), moderate criteria
        elif value_len >= 16:
            if separator_ratio < 0.25:
                # Need mixed case or digits to indicate randomness
                if (has_mixed_case and has_digits) or (has_digits and alnum_ratio > 0.90):
                    return True
        # For shorter values (12-15), require strict criteria
        elif value_len >= 12:
            if separator_ratio < 0.20:
                # Must have both mixed case and digits for short values
                if has_mixed_case and has_digits and alnum_ratio > 0.90:
                    return True
    
    return False


def _generate_placeholder(key):
    """Generate a human-readable placeholder for a key."""
    # Remove common prefixes/suffixes
    clean_key = key.strip()
    
    # Convert to placeholder format
    placeholder = clean_key.replace('_', '_').upper()
    
    # Add YOUR_ prefix if not already present
    if not placeholder.startswith('YOUR_'):
        placeholder = f'YOUR_{placeholder}'
    
    return placeholder


def _parse_env_line(line):
    """Parse a single line from .env file.
    
    Returns:
        tuple: (is_comment_or_blank, key, value, original_line)
    """
    original = line
    stripped = line.strip()
    
    # Blank line
    if not stripped:
        return (True, None, None, original)
    
    # Comment line
    if stripped.startswith('#'):
        return (True, None, None, original)
    
    # Export statement
    if stripped.startswith('export '):
        # Parse: export KEY=value
        export_part = stripped[7:].strip()
        if '=' in export_part:
            # Find first = that's not inside quotes
            eq_pos = -1
            in_quotes = False
            quote_char = None
            for i, char in enumerate(export_part):
                if char in ('"', "'") and (i == 0 or export_part[i-1] != '\\'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                elif char == '=' and not in_quotes:
                    eq_pos = i
                    break
            
            if eq_pos > 0:
                key = export_part[:eq_pos].strip()
                value = export_part[eq_pos+1:]
                return (False, key, value, original)
        return (True, None, None, original)
    
    # Regular KEY=value
    if '=' in stripped:
        # Find first = that's not inside quotes
        eq_pos = -1
        in_quotes = False
        quote_char = None
        for i, char in enumerate(stripped):
            if char in ('"', "'") and (i == 0 or stripped[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
            elif char == '=' and not in_quotes:
                eq_pos = i
                break
        
        if eq_pos > 0:
            key_part = stripped[:eq_pos].strip()
            value_part = stripped[eq_pos+1:]
            
            # Handle inline comments: KEY=value # comment
            # Only if # is not inside quotes
            if ' #' in value_part:
                comment_pos = value_part.find(' #')
                # Check if # is inside quotes
                in_quotes_check = False
                quote_char_check = None
                for i, char in enumerate(value_part[:comment_pos]):
                    if char in ('"', "'") and (i == 0 or value_part[i-1] != '\\'):
                        if not in_quotes_check:
                            in_quotes_check = True
                            quote_char_check = char
                        elif char == quote_char_check:
                            in_quotes_check = False
                            quote_char_check = None
                
                if not in_quotes_check:
                    value_part = value_part[:comment_pos]
            
            return (False, key_part, value_part, original)
    
    # Line doesn't match expected format, preserve as-is
    return (True, None, None, original)


def _format_output_line(key, placeholder, original_line):
    """Format a line for output, preserving original formatting where possible."""
    stripped = original_line.strip()
    
    # Preserve export statements
    if stripped.startswith('export '):
        # Preserve original newline
        newline = '\n' if original_line.endswith('\n') else ''
        return f"export {key}={placeholder}{newline}"
    
    # Check for inline comments (but only if # is not in quotes)
    if ' #' in original_line:
        # Simple check: if the # appears after the value part
        comment_pos = original_line.find(' #')
        # Basic heuristic: if there are quotes before #, might be in value
        # For simplicity, preserve the comment
        comment_part = original_line[comment_pos:]
        newline = '\n' if original_line.endswith('\n') else ''
        return f"{key}={placeholder}{comment_part}{newline}" if comment_part.endswith('\n') else f"{key}={placeholder}{comment_part}\n"
    
    # Preserve leading whitespace and newline
    leading_ws = original_line[:len(original_line) - len(original_line.lstrip())]
    newline = '\n' if original_line.endswith('\n') else ''
    return f"{leading_ws}{key}={placeholder}{newline}"


def create_safe_example(input_path, output_path=None):
    """Create a safe .env.example file from a .env file.
    
    Args:
        input_path: Path to input .env file
        output_path: Path to output .env.example file (default: input_path + '.example')
    
    Returns:
        int: Number of secrets replaced
    
    Raises:
        TypeError: If input_path or output_path is not a string
        ValueError: If input_path or output_path is empty
        FileNotFoundError: If input file doesn't exist or output directory doesn't exist
        IsADirectoryError: If input_path or output_path is a directory
        PermissionError: If file cannot be read or written
        UnicodeDecodeError: If input file encoding is invalid
        UnicodeEncodeError: If output file encoding fails
        OSError: For other file system errors
    """
    # Validate input path BEFORE any string operations
    if not isinstance(input_path, str):
        raise TypeError(f"Input path must be a string, got {type(input_path).__name__}")
    if not input_path:
        raise ValueError("Input path cannot be empty")
    
    if output_path is None:
        output_path = input_path + '.example'
    else:
        # Validate output path if provided
        if not isinstance(output_path, str):
            raise TypeError(f"Output path must be a string, got {type(output_path).__name__}")
        if not output_path:
            raise ValueError("Output path cannot be empty")
    
    secrets_replaced = 0
    
    # Read input file with comprehensive error handling
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except IsADirectoryError:
        raise IsADirectoryError(f"Input path is a directory, not a file: {input_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot read {input_path}")
    except UnicodeDecodeError as e:
        # Preserve original exception with better message
        raise UnicodeDecodeError(
            e.encoding, e.object, e.start, e.end,
            f"Cannot decode file {input_path}: {e.reason}. File may not be UTF-8 encoded."
        ) from e
    except OSError as e:
        raise OSError(f"Error reading file {input_path}: {e}") from e
    
    # Pre-allocate output list with estimated size (header + lines)
    output_lines = []
    output_lines.append("# WARNING: Do not add real secrets to this file!\n")
    output_lines.append("# This is an example file with placeholders.\n")
    output_lines.append("# Copy this file to .env and fill in your actual values.\n")
    output_lines.append("\n")
    
    # Process lines
    for line in lines:
        is_comment_or_blank, key, value, original = _parse_env_line(line)
        
        if is_comment_or_blank:
            # Preserve comments and blank lines as-is
            output_lines.append(original)
            continue
        
        # Check if this should be replaced based solely on value characteristics
        # No hardcoded patterns or keywords - pure heuristic analysis
        if value and _is_secret_value(value):
            placeholder = _generate_placeholder(key)
            output_lines.append(_format_output_line(key, placeholder, original))
            secrets_replaced += 1
        else:
            # Keep safe values as-is
            output_lines.append(original)
    
    # Write output file with comprehensive error handling
    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(output_lines)
    except IsADirectoryError:
        raise IsADirectoryError(f"Output path is a directory, not a file: {output_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot write to {output_path}")
    except UnicodeEncodeError as e:
        raise UnicodeEncodeError(
            e.encoding, e.object, e.start, e.end,
            f"Cannot encode data when writing to {output_path}: {e.reason}"
        ) from e
    except FileNotFoundError:
        # Output directory doesn't exist
        raise FileNotFoundError(
            f"Output directory does not exist for: {output_path}. "
            f"Please create the directory first."
        )
    except OSError as e:
        raise OSError(f"Error writing file {output_path}: {e}") from e
    
    return secrets_replaced


def validate_segment(segment_definition):
    """Validate a segment definition - ENHANCED VERSION"""
    errors = []
    
    if not segment_definition:
        errors.append("Segment definition is missing")
        return False
    
    # Check required fields
    segment_name = segment_definition.get('name', '').strip()
    if not segment_name or segment_name == 'New Segment':
        errors.append("Segment name is required and cannot be 'New Segment'")
    
    # Check for at least one container
    containers = segment_definition.get('containers', [])
    if not containers:
        errors.append("At least one container is required")
        return False  # Can't continue validation without containers
    
    # Validate each container
    has_valid_conditions = False
    for idx, container in enumerate(containers):
        container_errors = validate_container(container, idx)
        errors.extend(container_errors)
        
        # Check if this container has valid conditions
        if container.get('conditions'):
            has_valid_conditions = True
    
    if not has_valid_conditions:
        errors.append("At least one container must have conditions")
    
    # Validate container hierarchy
    hierarchy_errors = validate_container_hierarchy(segment_definition)
    errors.extend(hierarchy_errors)
    
    # Return True if no errors
    if errors:
        print(f"Validation errors: {errors}")  # Debug output
        return False
    return True

def validate_container(container, container_idx):
    """Validate a single container - ENHANCED VERSION"""
    errors = []
    
    if not container:
        errors.append(f"Container {container_idx + 1}: Container is empty")
        return errors
    
    # Check container type
    valid_types = ['hit', 'visit', 'visitor']
    container_type = container.get('type')
    if container_type not in valid_types:
        errors.append(f"Container {container_idx + 1}: Invalid container type '{container_type}'. Must be one of: {valid_types}")
    
    # Check include/exclude
    include = container.get('include')
    if include not in [True, False]:
        errors.append(f"Container {container_idx + 1}: Include must be True or False")
    
    # Check for conditions
    conditions = container.get('conditions', [])
    if not conditions:
        errors.append(f"Container {container_idx + 1}: At least one condition is required")
    else:
        # Validate each condition
        for idx, condition in enumerate(conditions):
            condition_errors = validate_condition(condition, container_idx, idx)
            errors.extend(condition_errors)
    
    return errors

def validate_condition(condition, container_idx, condition_idx):
    """Validate a single condition - ENHANCED VERSION"""
    errors = []
    
    if not condition:
        errors.append(f"Container {container_idx + 1}, Condition {condition_idx + 1}: Condition is empty")
        return errors
    
    # Check field
    field = condition.get('field', '').strip()
    if not field:
        errors.append(f"Container {container_idx + 1}, Condition {condition_idx + 1}: Field is required")
    
    # Check operator
    operator = condition.get('operator', '').strip()
    if not operator:
        errors.append(f"Container {container_idx + 1}, Condition {condition_idx + 1}: Operator is required")
    
    # Check value (except for exists/not exists operators)
    if operator not in ['exists', 'does not exist']:
        value = condition.get('value')
        if value is None or str(value).strip() == '':
            errors.append(f"Container {container_idx + 1}, Condition {condition_idx + 1}: Value is required for operator '{operator}'")
    
    # For between operator, check second value
    if operator == 'is between':
        value2 = condition.get('value2')
        if value2 is None or str(value2).strip() == '':
            errors.append(f"Container {container_idx + 1}, Condition {condition_idx + 1}: Second value is required for 'between' operator")
    
    # Validate data type consistency
    data_type = condition.get('data_type', 'string')
    value = condition.get('value')
    
    if data_type == 'number' and value is not None and str(value).strip():
        try:
            float(str(value))
        except (ValueError, TypeError):
            errors.append(f"Container {container_idx + 1}, Condition {condition_idx + 1}: Value must be a number for numeric fields")
    
    # Validate operator compatibility with data type
    string_operators = ['equals', 'does not equal', 'contains', 'does not contain', 'starts with', 'ends with', 'exists', 'does not exist']
    number_operators = ['equals', 'does not equal', 'is greater than', 'is less than', 'is greater than or equal to', 'is less than or equal to', 'is between', 'exists', 'does not exist']
    
    if data_type == 'string' and operator not in string_operators:
        errors.append(f"Container {container_idx + 1}, Condition {condition_idx + 1}: Operator '{operator}' is not valid for string fields")
    elif data_type == 'number' and operator not in number_operators:
        errors.append(f"Container {container_idx + 1}, Condition {condition_idx + 1}: Operator '{operator}' is not valid for number fields")
    
    return errors

def validate_container_hierarchy(segment_definition):
    """Validate container hierarchy rules including nested levels"""
    errors = []

    if not segment_definition:
        return errors

    container_levels = {'hit': 1, 'visit': 2, 'visitor': 3}
    main_level = container_levels.get(segment_definition.get('container_type', 'hit'), 1)

    def _check(cont, parent_level, path):
        c_type = cont.get('type', 'hit')
        level = container_levels.get(c_type, 1)
        if level > parent_level:
            errors.append(f"Container {path}: Cannot nest {c_type} inside level {parent_level}")
        for idx, child in enumerate(cont.get('children', [])):
            _check(child, level, f"{path}.{idx+1}")

    for idx, container in enumerate(segment_definition.get('containers', [])):
        _check(container, main_level, str(idx + 1))

    return errors

def sanitize_segment_name(name):
    """Sanitize segment name for safe storage - ENHANCED VERSION"""
    import re
    
    if not name:
        return "Unnamed Segment"
    
    # Remove special characters, keep only alphanumeric, spaces, and basic punctuation
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_().]', '', str(name))
    
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Limit length
    sanitized = sanitized[:100]
    
    # Ensure it's not empty after sanitization
    result = sanitized.strip()
    if not result:
        result = "Unnamed Segment"
    
    return result

def validate_sql_injection(value):
    """Enhanced SQL injection prevention"""
    if value is None:
        return True, "Safe"
    
    dangerous_patterns = [
        'drop table', 'drop database', 'delete from', 'insert into', 
        'update set', 'create table', 'alter table', 'truncate',
        '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute',
        'union select', 'script', 'javascript:', 'vbscript:',
        'onload=', 'onerror=', '<script', '</script>'
    ]
    
    value_lower = str(value).lower()
    for pattern in dangerous_patterns:
        if pattern in value_lower:
            return False, f"Potentially dangerous pattern detected: {pattern}"
    
    # Check for excessive special characters
    special_chars = [';', "'", '"', '<', '>', '&', '|']
    special_count = sum(value_lower.count(char) for char in special_chars)
    if special_count > 5:  # Threshold for suspicious input
        return False, "Too many special characters detected"
    
    return True, "Safe"

def validate_field_name(field_name, config):
    """Validate that a field name exists in the configuration"""
    if not field_name:
        return False, "Field name is required"
    
    # Check dimensions
    for category in config.get('dimensions', []):
        for item in category['items']:
            if item['field'] == field_name:
                return True, "Valid dimension field"
    
    # Check metrics
    for category in config.get('metrics', []):
        for item in category['items']:
            if item['field'] == field_name:
                return True, "Valid metric field"
    
    return False, f"Field '{field_name}' not found in configuration"

def validate_operator_for_field(operator, field_name, config):
    """Validate that an operator is appropriate for a given field"""
    
    # Get field info
    field_info = get_field_info(field_name, config)
    if not field_info:
        return False, f"Field '{field_name}' not found"
    
    data_type = field_info.get('type', 'string')
    
    string_operators = ['equals', 'does not equal', 'contains', 'does not contain', 
                       'starts with', 'ends with', 'exists', 'does not exist']
    number_operators = ['equals', 'does not equal', 'is greater than', 'is less than', 
                       'is greater than or equal to', 'is less than or equal to', 
                       'is between', 'exists', 'does not exist']
    
    if data_type == 'string' and operator not in string_operators:
        return False, f"Operator '{operator}' is not valid for string field '{field_name}'"
    elif data_type == 'number' and operator not in number_operators:
        return False, f"Operator '{operator}' is not valid for number field '{field_name}'"
    
    return True, "Valid operator for field"

def get_field_info(field_name, config):
    """Get information about a field from the configuration"""
    
    # Check dimensions
    for category in config.get('dimensions', []):
        for item in category['items']:
            if item['field'] == field_name:
                return {
                    'name': item['name'],
                    'field': item['field'],
                    'type': item.get('type', 'string'),
                    'category': category['category'],
                    'field_type': 'dimension'
                }
    
    # Check metrics
    for category in config.get('metrics', []):
        for item in category['items']:
            if item['field'] == field_name:
                return {
                    'name': item['name'],
                    'field': item['field'],
                    'type': item.get('type', 'number'),
                    'category': category['category'],
                    'field_type': 'metric'
                }
    
    return None

def validate_value_format(value, data_type, operator):
    """Validate that a value is in the correct format for its data type and operator"""
    
    if operator in ['exists', 'does not exist']:
        return True, "No value required for existence operators"
    
    if value is None or str(value).strip() == '':
        return False, "Value is required for this operator"
    
    if data_type == 'number':
        try:
            float(str(value))
            return True, "Valid number"
        except (ValueError, TypeError):
            return False, "Value must be a valid number"
    
    # For string values, most formats are acceptable
    # But check for reasonable length
    if len(str(value)) > 1000:
        return False, "Value is too long (max 1000 characters)"
    
    return True, "Valid value format"

def get_validation_summary(segment_definition):
    """Get a comprehensive validation summary"""
    
    summary = {
        'is_valid': False,
        'errors': [],
        'warnings': [],
        'container_count': 0,
        'condition_count': 0,
        'complexity': 'unknown'
    }
    
    if not segment_definition:
        summary['errors'].append("No segment definition provided")
        return summary
    
    # Basic validation
    is_valid = validate_segment(segment_definition)
    summary['is_valid'] = is_valid
    
    # Count containers and conditions
    containers = segment_definition.get('containers', [])
    summary['container_count'] = len(containers)
    summary['condition_count'] = sum(len(c.get('conditions', [])) for c in containers)
    
    # Complexity analysis
    from src.utils.query_builder import analyze_segment_complexity
    try:
        complexity_info = analyze_segment_complexity(segment_definition)
        summary['complexity'] = complexity_info.get('complexity', 'unknown')
    except:
        summary['complexity'] = 'unknown'
    
    # Additional warnings
    if summary['container_count'] == 0:
        summary['warnings'].append("No containers defined")
    elif summary['condition_count'] == 0:
        summary['warnings'].append("No conditions defined")
    
    # Check for complex nested logic
    if summary['container_count'] > 3:
        summary['warnings'].append("Complex segment with many containers may be slow")
    
    return summary
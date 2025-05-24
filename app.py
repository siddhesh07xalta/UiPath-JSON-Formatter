import streamlit as st
import json
import re

st.set_page_config(page_title="UIPath JSON Formatter", layout="wide")

st.title("UIPath JSON Formatter")
st.markdown("""
This tool converts standard JSON into a format compatible with UIPath HTTP Request body property.
It handles variable references properly by replacing them with the appropriate C#-style syntax.
""")

# Example for demonstration
example_input = '''{ 
    "contents": [ 
        { 
            "parts": [ 
                { 
                    "text": MyVariable,
                    "id": UserID.ToString(),
                    "count": CountVar
                } 
            ] 
        } 
    ] 
}'''

example_output = '''"{""contents"": [{""parts"": [{""text"": " + MyVariable + ",""id"": " + UserID.ToString() + ",""count"": " + CountVar + "}]}]}"'''

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input JSON")
    input_json = st.text_area("Paste your JSON here:", example_input, height=300)

def format_for_uipath(input_text):
    try:
        # Remove extra whitespace and normalize the input
        normalized_text = re.sub(r'\s+', ' ', input_text.strip())
        
        # Find all potential variables (not quoted strings, not numbers, not booleans)
        # Pattern to match: key: value where value is not quoted, not a number, not boolean
        variable_pattern = r':\s*([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_().]+)*)\s*(?=[,}\]])'
        
        # Find all variables
        variables = re.findall(variable_pattern, normalized_text)
        
        # Start processing the text
        result = normalized_text
        
        # Replace each variable with the UIPath format
        for var in set(variables):  # Use set to avoid duplicates
            # Create pattern to match the variable in context
            pattern = f'(:\\s*){re.escape(var)}(\\s*[,}}\\]])'
            replacement = f'\\1" + {var} + "\\2'
            result = re.sub(pattern, replacement, result)
        
        # Handle edge cases where we might have empty strings
        result = re.sub(r'"\s*\+\s*"', '', result)  # Remove empty concatenations
        result = re.sub(r'\+\s*""\s*\+', ' + ', result)  # Clean up empty string concatenations
        
        # Double all remaining quotes for UIPath
        result = result.replace('"', '""')
        
        # Wrap the entire string in quotes
        result = '"' + result + '"'
        
        # Clean up any malformed concatenations
        result = re.sub(r'""""\s*\+\s*', '"" + ', result)
        result = re.sub(r'\+\s*""""', ' + ""', result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error processing JSON: {str(e)}")

def validate_json_structure(input_text):
    """Validate if the input has proper JSON structure"""
    try:
        # Try to parse as JSON first (this will fail if variables are present, but that's ok)
        json.loads(input_text)
        return True, "Valid JSON structure"
    except json.JSONDecodeError:
        # Check if it looks like JSON with variables
        if '{' in input_text and '}' in input_text:
            return True, "JSON-like structure with variables detected"
        else:
            return False, "Invalid JSON structure"

# Process button
process_button = st.button("Format JSON")

with col2:
    st.subheader("Formatted Result (UIPath Compatible)")
    
    if process_button:
        try:
            # Validate input structure
            is_valid, validation_msg = validate_json_structure(input_json)
            
            if not is_valid:
                st.error(f"Input validation failed: {validation_msg}")
                st.error("Please check your JSON structure and try again.")
            else:
                # Format the input JSON
                formatted_result = format_for_uipath(input_json)
                st.text_area("Copy this to UIPath:", formatted_result, height=300)
                
                st.success("JSON formatted successfully!")
                
                # Show usage instructions
                st.info("In UIPath, paste this result directly in the 'Body' property of an HTTP Request activity.")
                
                # Show detected variables
                variable_pattern = r':\s*([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_().]+)*)\s*(?=[,}\]])'
                variables = re.findall(variable_pattern, input_json)
                if variables:
                    st.info(f"Detected variables: {', '.join(set(variables))}")
            
        except Exception as e:
            st.error(f"Error formatting JSON: {str(e)}")
            st.error("Please check your input JSON syntax and try again.")
    else:
        # Show example output
        st.text_area("Example output:", example_output, height=300)

# Explanation section
st.markdown("""
### How UIPath JSON Formatting Works

When using HTTP Request activities in UIPath, JSON data needs special formatting:

1. **String Literal**: The entire JSON must be wrapped in quotes: `"..."`
2. **Escape Quotes**: All quotes inside the JSON must be doubled: `"` becomes `""`
3. **Variable References**: Variables are injected using string concatenation: `" + VariableName + "`

### Variable Detection Rules:

- Variables must start with a letter or underscore
- Can contain letters, numbers, underscores
- Can include property access with dots (e.g., `User.Name`, `Count.ToString()`)
- Must not be enclosed in quotes in the original JSON

### Example Transformations:

```
Original: "name": MyVariable
UIPath:   ""name"": "" + MyVariable + ""

Original: "id": User.ID.ToString()
UIPath:   ""id"": "" + User.ID.ToString() + ""
```
""")

# Additional help
with st.expander("Common Issues and Solutions"):
    st.markdown("""
    **Issue 1: Variables not detected**
    - Make sure variables are not enclosed in quotes
    - Variable names must start with letter/underscore
    - Use proper JSON structure with colons and commas
    
    **Issue 2: Formatting looks wrong**
    - The output should be one long string wrapped in quotes
    - All internal quotes are doubled for UIPath compatibility
    - Variables are concatenated using C# string concatenation syntax
    
    **Issue 3: UIPath gives syntax errors**
    - Ensure you're pasting into the Body property, not Body (Raw)
    - Make sure the HTTP Request activity Content Type is set correctly
    - Check that variable names match exactly in your UIPath workflow
    """)

with st.expander("Testing Your Variables"):
    st.markdown("""
    Before using the formatted JSON in UIPath:
    
    1. **Verify Variable Names**: Make sure all detected variables exist in your UIPath workflow
    2. **Check Data Types**: Ensure variables contain the expected data types
    3. **Test with Sample Data**: Use Write Line activities to verify variable contents
    4. **Validate JSON Structure**: Use online JSON validators to check your base structure
    """)

# Debug section
with st.expander("Debug Information"):
    if input_json.strip():
        st.write("**Input Analysis:**")
        variable_pattern = r':\s*([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_().]+)*)\s*(?=[,}\]])'
        variables = re.findall(variable_pattern, input_json)
        st.write(f"Detected variables: {list(set(variables))}")
        
        is_valid, validation_msg = validate_json_structure(input_json)
        st.write(f"Structure validation: {validation_msg}")
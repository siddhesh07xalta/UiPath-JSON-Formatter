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
                    "text": MyVariable 
                } 
            ] 
        } 
    ] 
}'''

example_output = '''{ 
    ""contents"": [ 
        { 
            ""parts"": [ 
                { 
                    ""text"": "+MyVariable+"
                } 
            ] 
        } 
    ] 
}'''

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input JSON")
    input_json = st.text_area("Paste your JSON here:", example_input, height=300)

# Function to process JSON and handle variable references
def format_for_uipath(input_text):
    # First pass: Identify variable names (not in quotes, not numbers)
    variables = re.findall(r':\s*([A-Za-z][A-Za-z0-9_]*)\s*[,}\]]', input_text)
    variables_with_properties = re.findall(r':\s*([A-Za-z][A-Za-z0-9_]*\.[A-Za-z0-9_.]+)\s*[,}\]]', input_text)
    variables.extend(variables_with_properties)
    
    # Create a copy of the input for modification
    formatted_text = input_text
    
    # Replace variables with C# string concatenation syntax
    for var in variables:
        # Look for the variable followed by comma, closing brace or bracket
        pattern = f':\\s*{var}\\s*([,}}\\]])'
        replacement = f': "+{var}+"\\1'
        formatted_text = re.sub(pattern, replacement, formatted_text)
    
    # Double all quotes
    formatted_text = formatted_text.replace('"', '""')
    
    # Wrap in quotes
    formatted_text = '"' + formatted_text + '"'
    
    return formatted_text

# Process button
process_button = st.button("Format JSON")

with col2:
    st.subheader("Formatted Result (UIPath Compatible)")
    
    if process_button:
        try:
            # Format the input JSON
            formatted_result = format_for_uipath(input_json)
            st.text_area("Copy this to UIPath:", formatted_result, height=300)
            
            st.success("JSON formatted successfully!")
            
            # Show usage instructions
            st.info("In UIPath, paste this result directly in the 'Body' property of an HTTP Request activity.")
            
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

1. **String Literal**: Start with `"` and end with `"`
2. **Double Quotes**: All quotes inside the JSON must be doubled (`"` becomes `""`)
3. **Variable References**: Variables are wrapped in `"+Variable+"` syntax for string concatenation

### Common Issues This Tool Solves:

- Properly escapes quotes in JSON for UIPath
- Correctly identifies and formats variable references
- Maintains proper formatting with indentation
- Handles nested objects and arrays
""")

# Additional help
with st.expander("Why is this formatting needed?"):
    st.markdown("""
    UIPath uses C# as its underlying language. In C#, string literals follow different rules than standard JSON:
    
    1. To include a double quote in a string, you need to double it (`""`)
    2. To include variables, C# uses string concatenation with the `+` operator
    
    Without this formatting, UIPath would interpret the JSON incorrectly, causing request failures.
    """)
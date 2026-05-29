from google.genai import types
import inspect

print("HttpOptions class attributes and doc:")
print(inspect.getdoc(types.HttpOptions))

# Check fields in types.HttpOptions
print("\nFields:")
for name, field in types.HttpOptions.model_fields.items():
    print(f"  {name}: {field.annotation}")

# JSON Import Guide

## Overview

The Problems Validator platform supports importing assignments from JSON files. This allows teachers to bulk-create assignments with all tasks and test cases in a single operation, rather than manually entering each component through the web interface.

## Import Methods

### 1. Web Interface

1. Log in as a teacher
2. Navigate to the dashboard
3. Click "Import from JSON" button
4. Select your JSON file
5. Click "Import Assignment"

### 2. Command Line Interface

Use the Django management command:

```bash
python manage.py import_assignment <file_path> --teacher <username>
```

**Options:**
- `file_path` - Path to the JSON file (required)
- `--teacher` - Username of the teacher who will own the assignment (required)
- `--verbose` - Enable detailed output (optional)

**Example:**
```bash
python manage.py import_assignment assignment_format.json --teacher admin --verbose
```

## JSON Format Specification

### Root Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Assignment title |
| `description` | string | No | Assignment description |
| `start_time` | string (ISO 8601) | No | When the assignment becomes available |
| `end_time` | string (ISO 8601) | No | When the assignment closes |
| `tasks` | array | Yes | Array of task objects |

### Task Object

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | Yes | - | Task title |
| `description` | string | Yes | - | Task description/instructions |
| `task_type` | string | No | "CODING" | Either "CODING" or "DESCRIPTION_ONLY" |
| `validation_type` | string | No | "MANUAL" | Either "AUTO" or "MANUAL" |
| `order` | number | No | 0 | Display order (lower numbers appear first) |
| `test_cases` | array | No | [] | Array of test case objects |

### Test Case Object

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `input_data` | string | No | "" | Input to pass to the script via stdin |
| `expected_output` | string | Yes | - | Expected output from stdout |

## Complete Example

```json
{
  "title": "Python Programming Basics",
  "description": "This assignment covers fundamental Python programming concepts including input/output, arithmetic operations, and conditional statements.",
  "start_time": "2026-02-15T10:00:00Z",
  "end_time": "2026-02-20T23:59:59Z",
  "tasks": [
    {
      "title": "Sum of Two Numbers",
      "description": "Write a Python program that reads two integers from input and prints their sum.\n\nInput Format:\nTwo integers on separate lines\n\nOutput Format:\nA single integer representing the sum",
      "task_type": "CODING",
      "validation_type": "AUTO",
      "order": 1,
      "test_cases": [
        {
          "input_data": "5\n3\n",
          "expected_output": "8"
        },
        {
          "input_data": "10\n20\n",
          "expected_output": "30"
        },
        {
          "input_data": "-5\n5\n",
          "expected_output": "0"
        }
      ]
    },
    {
      "title": "Even or Odd",
      "description": "Write a Python program that reads an integer and prints 'Even' if it's even, or 'Odd' if it's odd.",
      "task_type": "CODING",
      "validation_type": "AUTO",
      "order": 2,
      "test_cases": [
        {
          "input_data": "4\n",
          "expected_output": "Even"
        },
        {
          "input_data": "7\n",
          "expected_output": "Odd"
        }
      ]
    },
    {
      "title": "Essay Question",
      "description": "Explain the difference between a list and a tuple in Python. Provide examples of when you would use each data structure.",
      "task_type": "DESCRIPTION_ONLY",
      "validation_type": "MANUAL",
      "order": 3
    }
  ]
}
```

## Important Notes

### Date/Time Format

- Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `2026-02-15T10:00:00Z`
- The `Z` suffix indicates UTC timezone
- Both `start_time` and `end_time` are optional

### Newline Characters

- In JSON strings, use `\n` for newlines
- Example: `"5\n3\n"` represents two lines: "5" and "3"

### Task Types

- **CODING**: Students submit code that can be executed
- **DESCRIPTION_ONLY**: Students submit text answers (essays, explanations, etc.)

### Validation Types

- **AUTO**: Code is automatically validated against test cases
- **MANUAL**: Teacher manually grades the submission

### Test Cases

- Only relevant for tasks with `validation_type: "AUTO"`
- Each test case compares actual output with expected output
- Output comparison is exact (whitespace matters)

## Troubleshooting

### Common Errors

**"Missing required field: title"**
- Ensure your JSON has a `title` field at the root level

**"Invalid JSON format"**
- Validate your JSON using a tool like [jsonlint.com](https://jsonlint.com)
- Check for missing commas, brackets, or quotes

**"Invalid datetime format"**
- Use ISO 8601 format: `2026-02-15T10:00:00Z`
- Don't forget the `T` separator and `Z` suffix

**"User 'username' is not a teacher"**
- Ensure the specified user has teacher role and is approved
- Check user role in Django admin

### Validation

Before importing, you can validate your JSON:
1. Check syntax at [jsonlint.com](https://jsonlint.com)
2. Ensure all required fields are present
3. Verify datetime formats
4. Test with a small assignment first

## Tips

1. **Start Small**: Create a simple assignment with 1-2 tasks first to test the format
2. **Use Templates**: Copy `assignment_format.json` and modify it for your needs
3. **Escape Characters**: Remember to escape special characters in JSON strings
4. **Test Cases**: Add multiple test cases to cover edge cases
5. **Order Matters**: Use the `order` field to control task display sequence

## Support

If you encounter issues:
1. Check the error message carefully
2. Validate your JSON syntax
3. Ensure all required fields are present
4. Review this guide for format specifications

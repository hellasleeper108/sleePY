# PyQuest Content Generator

Automatically convert CSV files into PyQuest challenges and lessons. This tool makes it easy for educators to contribute new content to the platform without manually creating database entries.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Creating Challenges](#creating-challenges)
- [Creating Lessons](#creating-lessons)
- [CSV Format Reference](#csv-format-reference)
- [Examples](#examples)
- [Validation Rules](#validation-rules)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### 1. Prepare Your CSV File

Use the templates provided in `templates/`:
- `challenges_template.csv` - For coding challenges
- `lessons_template.csv` - For theory lessons

Or check out the examples in `examples/`:
- `challenges_example.csv` - 10 sample challenges
- `lessons_example.csv` - 7 sample lessons

### 2. Run the Generator

```bash
# Generate challenges
python content_generator.py challenges examples/challenges_example.csv

# Generate lessons
python content_generator.py lessons examples/lessons_example.csv

# Generate both
python content_generator.py both examples/challenges_example.csv examples/lessons_example.csv

# Specify custom output directory
python content_generator.py challenges my_challenges.csv -o output/
```

### 3. Import into Database

The generator creates:
- SQL files (`challenges.sql`)
- Python import scripts (`import_challenges.py`, `import_lessons.py`)
- Markdown lesson files (in `lessons_markdown/`)
- Summary statistics

To import:

```bash
# Option 1: Run Python import script (recommended)
cd generated/
python import_challenges.py
python import_lessons.py

# Option 2: Execute SQL directly
psql -U pyquest -d pyquest -f generated/challenges.sql
```

---

## 📝 Creating Challenges

### Challenge CSV Format

Create a CSV file with these columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| title | ✅ | Challenge title | "Hello World" |
| description | ✅ | Short description (1-2 sentences) | "Write a function that returns Hello World" |
| instructions | ✅ | Detailed instructions with examples | "Create a function called greet()..." |
| difficulty | ✅ | beginner, intermediate, advanced, expert | "beginner" |
| category | ✅ | basics, data_structures, algorithms, etc. | "basics" |
| xp_reward | ❌ | XP points (auto-calculated if empty) | 10 |
| required_level | ❌ | Minimum level (default: 1) | 1 |
| starter_code | ❌ | Initial code template | "def greet():\n    pass" |
| solution | ❌ | Sample solution | "def greet():\n    return 'Hello'" |
| test_cases | ❌ | JSON array of test cases | See below |
| learning_path | ❌ | Associated learning path | "Python Basics" |

### Test Cases Format

Test cases should be a JSON array:

```json
[
  {
    "input": "test_input",
    "expected_output": "expected_result",
    "description": "Test description"
  }
]
```

**Example:**

```json
[
  {"input": "2, 3", "expected_output": "5", "description": "2 + 3 should equal 5"},
  {"input": "10, -5", "expected_output": "5", "description": "10 + (-5) should equal 5"}
]
```

### Challenge Example

```csv
title,description,instructions,difficulty,category,xp_reward,required_level,starter_code,solution,test_cases,learning_path
"Sum Two Numbers","Calculate the sum of two numbers","Create a function called `add()` that takes two numbers and returns their sum.","beginner","basics",10,1,"def add(a, b):\n    pass","def add(a, b):\n    return a + b","[{""input"": ""2, 3"", ""expected_output"": ""5"", ""description"": ""2 + 3 = 5""}]",""
```

### XP Calculation

If you don't specify `xp_reward`, it's automatically calculated based on difficulty:

- **Beginner**: Base XP × 1.0 = 10 XP
- **Intermediate**: Base XP × 1.5 = 15 XP
- **Advanced**: Base XP × 2.0 = 20 XP
- **Expert**: Base XP × 3.0 = 30 XP

You can override this by providing a custom value.

---

## 📚 Creating Lessons

### Lesson CSV Format

Create a CSV file with these columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| learning_path | ✅ | Path this lesson belongs to | "Python Basics" |
| title | ✅ | Lesson title | "Variables and Types" |
| lesson_type | ✅ | theory, example, exercise, quiz | "theory" |
| order | ✅ | Display order (starts at 1) | 1 |
| content | ✅ | Lesson content in Markdown | See below |
| xp_reward | ❌ | XP points (default: 5) | 5 |
| estimated_minutes | ❌ | Estimated completion time | 10 |

### Markdown Content

Lessons support full Markdown formatting:

```markdown
# Main Heading

## Subheading

Regular paragraph text.

**Bold text** and *italic text*

- Bullet point 1
- Bullet point 2

1. Numbered item
2. Another item

\```python
# Code block
print("Hello, World!")
\```

> Quote or note
```

### Multi-line Content in CSV

Use `\n` for line breaks in your CSV:

```csv
"Variables in Python\n\nVariables store data.\n\n```python\nx = 5\n```"
```

### Lesson Example

```csv
learning_path,title,lesson_type,order,content,xp_reward,estimated_minutes
"Python Basics","Introduction to Python","theory",1,"# Welcome to Python!\n\nPython is easy to learn.\n\n```python\nprint('Hello')\n```",5,10
```

---

## 📖 CSV Format Reference

### Valid Difficulties

- `beginner` - For newcomers, simple concepts
- `intermediate` - Requires basic knowledge
- `advanced` - Complex topics, multiple concepts
- `expert` - Advanced algorithms, optimization

### Valid Categories

- `basics` - Variables, operators, control flow
- `data_structures` - Lists, dictionaries, sets
- `algorithms` - Sorting, searching, recursion
- `oop` - Classes, objects, inheritance
- `functional` - Functions, lambdas, map/filter
- `web` - Web development topics
- `data_science` - NumPy, Pandas, analysis
- `other` - Miscellaneous topics

### Valid Lesson Types

- `theory` - Conceptual explanation
- `example` - Code examples and demonstrations
- `exercise` - Practice problems
- `quiz` - Multiple choice or short answer

### Special Characters in CSV

- Use double quotes around fields containing commas
- Escape quotes inside fields by doubling them: `""`
- Use `\n` for newlines
- For test_cases JSON, escape quotes: `""{""input"": ""value""}""`

---

## 💡 Examples

### Example 1: Simple Challenge

```csv
title,description,instructions,difficulty,category,xp_reward,required_level,starter_code,solution,test_cases,learning_path
"Hello World","Write a function that returns Hello World","Create a function called greet() that returns 'Hello, World!'","beginner","basics",10,1,"def greet():\n    pass","def greet():\n    return 'Hello, World!'","[{""input"": """", ""expected_output"": ""Hello, World!"", ""description"": ""Should return Hello, World!""}]",""
```

### Example 2: Challenge with Multiple Test Cases

```csv
title,description,instructions,difficulty,category,xp_reward,required_level,starter_code,solution,test_cases,learning_path
"Even or Odd","Check if number is even","Create a function is_even() that returns True for even numbers","beginner","basics",15,1,"def is_even(n):\n    pass","def is_even(n):\n    return n % 2 == 0","[{""input"": ""4"", ""expected_output"": ""True"", ""description"": ""4 is even""}, {""input"": ""7"", ""expected_output"": ""False"", ""description"": ""7 is odd""}]",""
```

### Example 3: Theory Lesson

```csv
learning_path,title,lesson_type,order,content,xp_reward,estimated_minutes
"Python Basics","Variables","theory",1,"# Variables\n\nVariables store data:\n\n```python\nname = 'Alice'\nage = 25\n```\n\nUse descriptive names!",5,10
```

---

## ✅ Validation Rules

The generator validates all data before creating output files:

### Challenge Validation

- ✅ Title, description, and instructions are required
- ✅ Difficulty must be valid (beginner/intermediate/advanced/expert)
- ✅ Category must be valid (basics/data_structures/etc.)
- ✅ XP reward must be a number (or empty for auto-calculation)
- ✅ Required level must be a number
- ✅ Test cases must be valid JSON if provided

### Lesson Validation

- ✅ Learning path, title, and content are required
- ✅ Lesson type must be valid (theory/example/exercise/quiz)
- ✅ Order must be a number
- ✅ XP reward must be a number
- ✅ Estimated minutes must be a number if provided

### Error Messages

If validation fails, you'll get clear error messages:

```
❌ Validation Errors:
  Row 3: 'title' is required
  Row 5: Invalid difficulty 'easy'. Must be one of: beginner, intermediate, advanced, expert
  Row 7: 'xp_reward' must be a number
```

Fix the errors in your CSV and run the generator again.

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "Invalid difficulty"**
- **Solution**: Use lowercase: `beginner`, `intermediate`, `advanced`, or `expert`

**Issue: "Invalid JSON in test_cases"**
- **Solution**: Escape quotes properly: `""{""input"": ""value""}""`
- Check for missing commas, brackets, or quotes

**Issue: "Newlines not working in content"**
- **Solution**: Use `\n` in your CSV, not actual newlines

**Issue: "Learning path not found"**
- **Solution**: Make sure the learning path exists in the database before importing lessons

**Issue: "Commas breaking CSV"**
- **Solution**: Wrap the entire field in double quotes: `"field, with, commas"`

### Getting Help

1. Check the example CSV files in `examples/`
2. Review the templates in `templates/`
3. Run the generator with `-h` for help: `python content_generator.py -h`
4. Check the generated summary files for statistics

---

## 📊 Generated Files

After running the generator, you'll find:

### For Challenges

- `challenges.sql` - SQL INSERT statements
- `import_challenges.py` - Python import script (recommended)
- `challenges_summary.txt` - Statistics and summary

### For Lessons

- `lessons_markdown/` - Individual markdown files organized by path
- `import_lessons.py` - Python import script
- `lessons_summary.txt` - Statistics and summary

---

## 🎯 Best Practices

### Writing Challenges

1. **Clear Instructions**: Explain what the function should do, parameters, and return value
2. **Examples**: Include 2-3 examples showing expected behavior
3. **Test Cases**: Provide at least 3 test cases covering edge cases
4. **Starter Code**: Give a function signature to guide students
5. **Difficulty**: Be honest about difficulty - it affects XP and student experience

### Writing Lessons

1. **Structure**: Start with overview, build up concepts, end with practice
2. **Code Examples**: Include working code students can try
3. **Short Paragraphs**: Keep text readable, break into sections
4. **Progressive**: Order lessons from simple to complex
5. **XP Balance**: Theory lessons: 5 XP, Example lessons: 5 XP, Exercises: 10+ XP

### CSV Tips

1. **Test Small**: Start with 2-3 rows, verify output, then add more
2. **Use Examples**: Copy from `examples/` and modify
3. **Consistent Naming**: Keep category and path names consistent
4. **Backup**: Keep your CSV files in version control

---

## 🚀 Workflow

**Recommended workflow for adding new content:**

1. **Plan**: Decide on topic, difficulty, and learning objectives
2. **Create CSV**: Use templates, add 5-10 items at a time
3. **Generate**: Run `content_generator.py` to create output files
4. **Review**: Check generated summary and SQL/Python files
5. **Test**: Import into development database
6. **Verify**: Test challenges and lessons in the app
7. **Deploy**: Import into production database

---

## 📝 Contributing

To contribute new challenges or lessons:

1. Fork the repository
2. Create your CSV files in `content/examples/`
3. Run the generator to validate
4. Submit a pull request with your CSV files
5. Include the generated summary in your PR description

---

## 📄 License

This content generator is part of PyQuest and uses the same MIT license.

---

**Questions?** Open an issue on GitHub or contact the PyQuest team.

**Happy Content Creating!** 🎉

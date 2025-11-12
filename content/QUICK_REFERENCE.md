# Content Generator Quick Reference

## 🚀 Quick Commands

```bash
# Generate challenges
python content_generator.py challenges examples/challenges_example.csv

# Generate lessons
python content_generator.py lessons examples/lessons_example.csv

# Generate both
python content_generator.py both examples/challenges_example.csv examples/lessons_example.csv

# Custom output directory
python content_generator.py challenges my_challenges.csv -o output/

# Get help
python content_generator.py -h
```

## 📋 CSV Column Reference

### Challenges

| Column | Required | Values |
|--------|----------|--------|
| title | ✅ | Any text |
| description | ✅ | Short description |
| instructions | ✅ | Detailed text with \n for newlines |
| difficulty | ✅ | beginner, intermediate, advanced, expert |
| category | ✅ | basics, data_structures, algorithms, oop, functional, web, data_science, other |
| xp_reward | ❌ | Number (auto-calculated if empty) |
| required_level | ❌ | Number (default: 1) |
| starter_code | ❌ | Code with \n for newlines |
| solution | ❌ | Code with \n for newlines |
| test_cases | ❌ | JSON array: `[{"input": "", "expected_output": "", "description": ""}]` |
| learning_path | ❌ | Path name |

### Lessons

| Column | Required | Values |
|--------|----------|--------|
| learning_path | ✅ | Path name |
| title | ✅ | Any text |
| lesson_type | ✅ | theory, example, exercise, quiz |
| order | ✅ | Number (1, 2, 3...) |
| content | ✅ | Markdown with \n for newlines |
| xp_reward | ❌ | Number (default: 5) |
| estimated_minutes | ❌ | Number |

## 💾 XP Auto-Calculation

- **Beginner**: 10 XP (base × 1.0)
- **Intermediate**: 15 XP (base × 1.5)
- **Advanced**: 20 XP (base × 2.0)
- **Expert**: 30 XP (base × 3.0)

## 📝 CSV Tips

- Wrap fields with commas in double quotes
- Use `\n` for newlines (not actual newlines)
- Escape quotes in JSON: `""{""key"": ""value""}""`
- Start small (3-5 rows), then expand

## 🔍 Validation Errors

Common errors and fixes:

```
❌ Invalid difficulty 'easy'
✅ Use: beginner, intermediate, advanced, or expert

❌ 'xp_reward' must be a number
✅ Use: 10 or leave empty for auto-calculation

❌ Invalid JSON in 'test_cases'
✅ Check brackets, commas, and quote escaping
```

## 📂 Generated Files

### Challenges
- `challenges.sql` - SQL INSERT statements
- `import_challenges.py` - Python import script ⭐ (recommended)
- `challenges_summary.txt` - Statistics

### Lessons
- `lessons_markdown/` - Individual .md files
- `import_lessons.py` - Python import script ⭐ (recommended)
- `lessons_summary.txt` - Statistics

## 🎯 Import to Database

```bash
# Navigate to generated directory
cd generated/

# Run import scripts (recommended)
python import_challenges.py
python import_lessons.py

# Or use SQL
psql -U pyquest -d pyquest -f challenges.sql
```

## 📖 Need More Help?

- Full documentation: `README.md`
- Example challenges: `examples/challenges_example.csv`
- Example lessons: `examples/lessons_example.csv`
- Templates: `templates/`

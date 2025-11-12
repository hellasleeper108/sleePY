#!/usr/bin/env python3
"""
PyQuest Content Generator

Automatically converts CSV files into PyQuest challenges and lessons.
Allows educators to easily contribute new content to the platform.

Usage:
    python content_generator.py challenges examples/challenges.csv
    python content_generator.py lessons examples/lessons.csv
    python content_generator.py both examples/challenges.csv examples/lessons.csv
"""

import csv
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class ContentValidator:
    """Validates challenge and lesson data"""

    VALID_DIFFICULTIES = ['beginner', 'intermediate', 'advanced', 'expert']
    VALID_CATEGORIES = ['basics', 'data_structures', 'algorithms', 'oop',
                        'functional', 'web', 'data_science', 'other']
    VALID_LESSON_TYPES = ['theory', 'example', 'exercise', 'quiz']

    XP_MULTIPLIERS = {
        'beginner': 1.0,
        'intermediate': 1.5,
        'advanced': 2.0,
        'expert': 3.0
    }

    @staticmethod
    def validate_challenge(row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """Validate and transform challenge data"""
        errors = []

        # Required fields
        if not row.get('title', '').strip():
            errors.append(f"Row {row_num}: 'title' is required")

        if not row.get('description', '').strip():
            errors.append(f"Row {row_num}: 'description' is required")

        if not row.get('instructions', '').strip():
            errors.append(f"Row {row_num}: 'instructions' is required")

        # Difficulty validation
        difficulty = row.get('difficulty', '').lower().strip()
        if difficulty not in ContentValidator.VALID_DIFFICULTIES:
            errors.append(f"Row {row_num}: Invalid difficulty '{difficulty}'. "
                         f"Must be one of: {', '.join(ContentValidator.VALID_DIFFICULTIES)}")

        # Category validation
        category = row.get('category', '').lower().strip()
        if category not in ContentValidator.VALID_CATEGORIES:
            errors.append(f"Row {row_num}: Invalid category '{category}'. "
                         f"Must be one of: {', '.join(ContentValidator.VALID_CATEGORIES)}")

        # XP calculation
        xp_reward = row.get('xp_reward', '').strip()
        if xp_reward:
            try:
                xp_reward = int(xp_reward)
            except ValueError:
                errors.append(f"Row {row_num}: 'xp_reward' must be a number")
                xp_reward = None
        else:
            # Auto-calculate XP based on difficulty
            base_xp = 10
            multiplier = ContentValidator.XP_MULTIPLIERS.get(difficulty, 1.0)
            xp_reward = int(base_xp * multiplier)

        # Required level
        required_level = row.get('required_level', '1').strip()
        try:
            required_level = int(required_level)
        except ValueError:
            errors.append(f"Row {row_num}: 'required_level' must be a number")
            required_level = 1

        # Test cases validation
        test_cases = row.get('test_cases', '').strip()
        if test_cases:
            try:
                test_cases_obj = json.loads(test_cases)
                if not isinstance(test_cases_obj, list):
                    errors.append(f"Row {row_num}: 'test_cases' must be a JSON array")
            except json.JSONDecodeError as e:
                errors.append(f"Row {row_num}: Invalid JSON in 'test_cases': {e}")

        if errors:
            raise ValueError("\n".join(errors))

        return {
            'title': row['title'].strip(),
            'description': row['description'].strip(),
            'instructions': row['instructions'].strip().replace('\\n', '\n'),
            'difficulty': difficulty,
            'category': category,
            'xp_reward': xp_reward,
            'required_level': required_level,
            'starter_code': row.get('starter_code', '').strip().replace('\\n', '\n'),
            'solution': row.get('solution', '').strip().replace('\\n', '\n'),
            'test_cases': test_cases,
            'learning_path': row.get('learning_path', '').strip(),
            'is_active': True
        }

    @staticmethod
    def validate_lesson(row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """Validate and transform lesson data"""
        errors = []

        # Required fields
        if not row.get('learning_path', '').strip():
            errors.append(f"Row {row_num}: 'learning_path' is required")

        if not row.get('title', '').strip():
            errors.append(f"Row {row_num}: 'title' is required")

        if not row.get('content', '').strip():
            errors.append(f"Row {row_num}: 'content' is required")

        # Lesson type validation
        lesson_type = row.get('lesson_type', '').lower().strip()
        if lesson_type not in ContentValidator.VALID_LESSON_TYPES:
            errors.append(f"Row {row_num}: Invalid lesson_type '{lesson_type}'. "
                         f"Must be one of: {', '.join(ContentValidator.VALID_LESSON_TYPES)}")

        # Order validation
        order = row.get('order', '').strip()
        if not order:
            errors.append(f"Row {row_num}: 'order' is required")
        else:
            try:
                order = int(order)
            except ValueError:
                errors.append(f"Row {row_num}: 'order' must be a number")
                order = None

        # XP validation
        xp_reward = row.get('xp_reward', '5').strip()
        try:
            xp_reward = int(xp_reward)
        except ValueError:
            errors.append(f"Row {row_num}: 'xp_reward' must be a number")
            xp_reward = 5

        # Estimated minutes
        estimated_minutes = row.get('estimated_minutes', '').strip()
        if estimated_minutes:
            try:
                estimated_minutes = int(estimated_minutes)
            except ValueError:
                errors.append(f"Row {row_num}: 'estimated_minutes' must be a number")
                estimated_minutes = None
        else:
            estimated_minutes = None

        if errors:
            raise ValueError("\n".join(errors))

        return {
            'learning_path': row['learning_path'].strip(),
            'title': row['title'].strip(),
            'lesson_type': lesson_type,
            'order': order,
            'content': row['content'].strip().replace('\\n', '\n'),
            'xp_reward': xp_reward,
            'estimated_minutes': estimated_minutes
        }


class ChallengeGenerator:
    """Generates PyQuest challenges from validated data"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_sql(self, challenges: List[Dict[str, Any]]) -> str:
        """Generate SQL INSERT statements for challenges"""
        sql_parts = [
            "-- PyQuest Challenges",
            f"-- Generated: {datetime.now().isoformat()}",
            f"-- Total challenges: {len(challenges)}",
            "",
            "-- Insert challenges",
            ""
        ]

        for challenge in challenges:
            test_cases = challenge['test_cases'] if challenge['test_cases'] else 'NULL'
            if test_cases != 'NULL':
                test_cases = f"'{test_cases}'"

            starter_code = f"'{self._escape_sql(challenge['starter_code'])}'" if challenge['starter_code'] else 'NULL'
            solution = f"'{self._escape_sql(challenge['solution'])}'" if challenge['solution'] else 'NULL'

            sql = f"""INSERT INTO challenges (
    title, description, instructions, difficulty, category,
    xp_reward, required_level, starter_code, solution, test_cases, is_active
) VALUES (
    '{self._escape_sql(challenge['title'])}',
    '{self._escape_sql(challenge['description'])}',
    '{self._escape_sql(challenge['instructions'])}',
    '{challenge['difficulty']}',
    '{challenge['category']}',
    {challenge['xp_reward']},
    {challenge['required_level']},
    {starter_code},
    {solution},
    {test_cases},
    TRUE
);
"""
            sql_parts.append(sql)

        return "\n".join(sql_parts)

    def generate_python_script(self, challenges: List[Dict[str, Any]]) -> str:
        """Generate Python script to insert challenges using SQLAlchemy"""
        script_parts = [
            '"""',
            'PyQuest Challenge Import Script',
            f'Generated: {datetime.now().isoformat()}',
            f'Total challenges: {len(challenges)}',
            '',
            'Usage:',
            '    python import_challenges.py',
            '"""',
            '',
            'import sys',
            'sys.path.append("..")',
            '',
            'from app.db.session import SessionLocal',
            'from app.models.challenge import Challenge, DifficultyLevel, ChallengeCategory',
            '',
            '',
            'def import_challenges():',
            '    """Import challenges from generated data"""',
            '    db = SessionLocal()',
            '    ',
            '    challenges = ['
        ]

        for challenge in challenges:
            script_parts.append('        {')
            script_parts.append(f"            'title': {repr(challenge['title'])},")
            script_parts.append(f"            'description': {repr(challenge['description'])},")
            script_parts.append(f"            'instructions': {repr(challenge['instructions'])},")
            script_parts.append(f"            'difficulty': DifficultyLevel.{challenge['difficulty'].upper()},")
            script_parts.append(f"            'category': ChallengeCategory.{challenge['category'].upper()},")
            script_parts.append(f"            'xp_reward': {challenge['xp_reward']},")
            script_parts.append(f"            'required_level': {challenge['required_level']},")
            script_parts.append(f"            'starter_code': {repr(challenge['starter_code']) if challenge['starter_code'] else 'None'},")
            script_parts.append(f"            'solution': {repr(challenge['solution']) if challenge['solution'] else 'None'},")
            script_parts.append(f"            'test_cases': {repr(challenge['test_cases']) if challenge['test_cases'] else 'None'},")
            script_parts.append(f"            'is_active': True")
            script_parts.append('        },')

        script_parts.extend([
            '    ]',
            '    ',
            '    try:',
            '        for challenge_data in challenges:',
            '            # Check if challenge already exists',
            '            existing = db.query(Challenge).filter(',
            '                Challenge.title == challenge_data["title"]',
            '            ).first()',
            '            ',
            '            if existing:',
            '                print(f"⚠️  Challenge \'{challenge_data[\'title\']}\' already exists, skipping...")',
            '                continue',
            '            ',
            '            challenge = Challenge(**challenge_data)',
            '            db.add(challenge)',
            '            print(f"✅ Added challenge: {challenge_data[\'title\']}")',
            '        ',
            '        db.commit()',
            '        print(f"\\n✅ Successfully imported {len(challenges)} challenges!")',
            '    except Exception as e:',
            '        print(f"❌ Error importing challenges: {e}")',
            '        db.rollback()',
            '        raise',
            '    finally:',
            '        db.close()',
            '',
            '',
            'if __name__ == "__main__":',
            '    import_challenges()',
        ])

        return "\n".join(script_parts)

    @staticmethod
    def _escape_sql(text: str) -> str:
        """Escape single quotes for SQL"""
        return text.replace("'", "''")

    def generate(self, challenges: List[Dict[str, Any]]):
        """Generate all challenge outputs"""
        # Generate SQL
        sql_file = self.output_dir / 'challenges.sql'
        sql_content = self.generate_sql(challenges)
        sql_file.write_text(sql_content)
        print(f"✅ Generated SQL: {sql_file}")

        # Generate Python import script
        py_file = self.output_dir / 'import_challenges.py'
        py_content = self.generate_python_script(challenges)
        py_file.write_text(py_content)
        print(f"✅ Generated Python script: {py_file}")

        # Generate summary
        summary_file = self.output_dir / 'challenges_summary.txt'
        summary = self._generate_summary(challenges)
        summary_file.write_text(summary)
        print(f"✅ Generated summary: {summary_file}")

    def _generate_summary(self, challenges: List[Dict[str, Any]]) -> str:
        """Generate summary statistics"""
        summary_parts = [
            "PyQuest Challenges Summary",
            f"Generated: {datetime.now().isoformat()}",
            f"Total challenges: {len(challenges)}",
            "",
            "By Difficulty:",
        ]

        # Count by difficulty
        difficulty_counts = {}
        category_counts = {}
        total_xp = 0

        for challenge in challenges:
            diff = challenge['difficulty']
            cat = challenge['category']
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1
            total_xp += challenge['xp_reward']

        for diff in ContentValidator.VALID_DIFFICULTIES:
            count = difficulty_counts.get(diff, 0)
            summary_parts.append(f"  {diff.capitalize()}: {count}")

        summary_parts.extend([
            "",
            "By Category:"
        ])

        for cat in ContentValidator.VALID_CATEGORIES:
            count = category_counts.get(cat, 0)
            if count > 0:
                summary_parts.append(f"  {cat.replace('_', ' ').title()}: {count}")

        summary_parts.extend([
            "",
            f"Total XP Available: {total_xp}",
            f"Average XP per Challenge: {total_xp // len(challenges) if challenges else 0}",
        ])

        return "\n".join(summary_parts)


class LessonGenerator:
    """Generates PyQuest lessons from validated data"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown_files(self, lessons: List[Dict[str, Any]]):
        """Generate markdown files for each lesson"""
        lessons_dir = self.output_dir / 'lessons_markdown'
        lessons_dir.mkdir(exist_ok=True)

        # Group by learning path
        paths = {}
        for lesson in lessons:
            path_name = lesson['learning_path']
            if path_name not in paths:
                paths[path_name] = []
            paths[path_name].append(lesson)

        # Generate files
        for path_name, path_lessons in paths.items():
            path_dir = lessons_dir / self._sanitize_filename(path_name)
            path_dir.mkdir(exist_ok=True)

            # Sort by order
            path_lessons.sort(key=lambda x: x['order'])

            for lesson in path_lessons:
                filename = f"{lesson['order']:02d}_{self._sanitize_filename(lesson['title'])}.md"
                filepath = path_dir / filename

                content = self._generate_lesson_markdown(lesson)
                filepath.write_text(content)
                print(f"✅ Generated lesson: {filepath}")

    def generate_python_script(self, lessons: List[Dict[str, Any]]) -> str:
        """Generate Python script to import lessons"""
        script_parts = [
            '"""',
            'PyQuest Lesson Import Script',
            f'Generated: {datetime.now().isoformat()}',
            f'Total lessons: {len(lessons)}',
            '',
            'Usage:',
            '    python import_lessons.py',
            '"""',
            '',
            'import sys',
            'sys.path.append("..")',
            '',
            'from app.db.session import SessionLocal',
            'from app.models.learning_path import LearningPath',
            'from app.models.lesson import Lesson, LessonType',
            '',
            '',
            'def import_lessons():',
            '    """Import lessons from generated data"""',
            '    db = SessionLocal()',
            '    ',
            '    # Group lessons by learning path',
            '    lessons_by_path = {}',
        ]

        # Group lessons
        paths = {}
        for lesson in lessons:
            path_name = lesson['learning_path']
            if path_name not in paths:
                paths[path_name] = []
            paths[path_name].append(lesson)

        for path_name in paths:
            script_parts.append(f"    lessons_by_path[{repr(path_name)}] = [")
            for lesson in paths[path_name]:
                script_parts.append('        {')
                script_parts.append(f"            'title': {repr(lesson['title'])},")
                script_parts.append(f"            'lesson_type': LessonType.{lesson['lesson_type'].upper()},")
                script_parts.append(f"            'order': {lesson['order']},")
                script_parts.append(f"            'content': {repr(lesson['content'])},")
                script_parts.append(f"            'xp_reward': {lesson['xp_reward']},")
                script_parts.append('        },')
            script_parts.append('    ]')

        script_parts.extend([
            '    ',
            '    try:',
            '        for path_name, lessons in lessons_by_path.items():',
            '            # Get or create learning path',
            '            learning_path = db.query(LearningPath).filter(',
            '                LearningPath.title == path_name',
            '            ).first()',
            '            ',
            '            if not learning_path:',
            '                print(f"⚠️  Learning path \'{path_name}\' not found, skipping lessons...")',
            '                continue',
            '            ',
            '            for lesson_data in lessons:',
            '                # Check if lesson already exists',
            '                existing = db.query(Lesson).filter(',
            '                    Lesson.learning_path_id == learning_path.id,',
            '                    Lesson.title == lesson_data["title"]',
            '                ).first()',
            '                ',
            '                if existing:',
            '                    print(f"⚠️  Lesson \'{lesson_data[\'title\']}\' already exists, skipping...")',
            '                    continue',
            '                ',
            '                lesson = Lesson(',
            '                    learning_path_id=learning_path.id,',
            '                    **lesson_data',
            '                )',
            '                db.add(lesson)',
            '                print(f"✅ Added lesson: {lesson_data[\'title\']}")',
            '        ',
            '        db.commit()',
            '        print(f"\\n✅ Successfully imported lessons!")',
            '    except Exception as e:',
            '        print(f"❌ Error importing lessons: {e}")',
            '        db.rollback()',
            '        raise',
            '    finally:',
            '        db.close()',
            '',
            '',
            'if __name__ == "__main__":',
            '    import_lessons()',
        ])

        return "\n".join(script_parts)

    def generate(self, lessons: List[Dict[str, Any]]):
        """Generate all lesson outputs"""
        # Generate markdown files
        self.generate_markdown_files(lessons)

        # Generate Python import script
        py_file = self.output_dir / 'import_lessons.py'
        py_content = self.generate_python_script(lessons)
        py_file.write_text(py_content)
        print(f"✅ Generated Python script: {py_file}")

        # Generate summary
        summary_file = self.output_dir / 'lessons_summary.txt'
        summary = self._generate_summary(lessons)
        summary_file.write_text(summary)
        print(f"✅ Generated summary: {summary_file}")

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize string for filename"""
        # Remove special characters
        name = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces with underscores
        name = re.sub(r'[-\s]+', '_', name)
        return name.lower()

    @staticmethod
    def _generate_lesson_markdown(lesson: Dict[str, Any]) -> str:
        """Generate markdown content for a lesson"""
        parts = [
            '---',
            f"title: {lesson['title']}",
            f"type: {lesson['lesson_type']}",
            f"order: {lesson['order']}",
            f"xp: {lesson['xp_reward']}",
        ]

        if lesson.get('estimated_minutes'):
            parts.append(f"estimated_minutes: {lesson['estimated_minutes']}")

        parts.extend([
            '---',
            '',
            lesson['content']
        ])

        return "\n".join(parts)

    def _generate_summary(self, lessons: List[Dict[str, Any]]) -> str:
        """Generate summary statistics"""
        summary_parts = [
            "PyQuest Lessons Summary",
            f"Generated: {datetime.now().isoformat()}",
            f"Total lessons: {len(lessons)}",
            "",
        ]

        # Group by learning path
        paths = {}
        type_counts = {}
        total_xp = 0

        for lesson in lessons:
            path = lesson['learning_path']
            ltype = lesson['lesson_type']

            if path not in paths:
                paths[path] = []
            paths[path].append(lesson)

            type_counts[ltype] = type_counts.get(ltype, 0) + 1
            total_xp += lesson['xp_reward']

        summary_parts.append("By Learning Path:")
        for path, path_lessons in sorted(paths.items()):
            summary_parts.append(f"  {path}: {len(path_lessons)} lessons")

        summary_parts.extend([
            "",
            "By Type:"
        ])

        for ltype in ContentValidator.VALID_LESSON_TYPES:
            count = type_counts.get(ltype, 0)
            if count > 0:
                summary_parts.append(f"  {ltype.capitalize()}: {count}")

        summary_parts.extend([
            "",
            f"Total XP Available: {total_xp}",
            f"Average XP per Lesson: {total_xp // len(lessons) if lessons else 0}",
        ])

        return "\n".join(summary_parts)


def process_challenges(csv_file: Path, output_dir: Path):
    """Process challenges CSV file"""
    print(f"\n📝 Processing challenges from: {csv_file}")

    challenges = []
    errors = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Skip comment lines
            lines = [line for line in f if not line.strip().startswith('#')]

            reader = csv.DictReader(lines)
            for i, row in enumerate(reader, start=2):  # Start at 2 (accounting for header)
                try:
                    challenge = ContentValidator.validate_challenge(row, i)
                    challenges.append(challenge)
                except ValueError as e:
                    errors.append(str(e))

    except FileNotFoundError:
        print(f"❌ Error: File not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        sys.exit(1)

    if errors:
        print("\n❌ Validation Errors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)

    if not challenges:
        print("⚠️  No challenges found in CSV file")
        sys.exit(0)

    print(f"✅ Validated {len(challenges)} challenges")

    # Generate outputs
    generator = ChallengeGenerator(output_dir)
    generator.generate(challenges)

    print(f"\n✅ Challenge generation complete!")
    print(f"📁 Output directory: {output_dir}")


def process_lessons(csv_file: Path, output_dir: Path):
    """Process lessons CSV file"""
    print(f"\n📝 Processing lessons from: {csv_file}")

    lessons = []
    errors = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Skip comment lines
            lines = [line for line in f if not line.strip().startswith('#')]

            reader = csv.DictReader(lines)
            for i, row in enumerate(reader, start=2):
                try:
                    lesson = ContentValidator.validate_lesson(row, i)
                    lessons.append(lesson)
                except ValueError as e:
                    errors.append(str(e))

    except FileNotFoundError:
        print(f"❌ Error: File not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        sys.exit(1)

    if errors:
        print("\n❌ Validation Errors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)

    if not lessons:
        print("⚠️  No lessons found in CSV file")
        sys.exit(0)

    print(f"✅ Validated {len(lessons)} lessons")

    # Generate outputs
    generator = LessonGenerator(output_dir)
    generator.generate(lessons)

    print(f"\n✅ Lesson generation complete!")
    print(f"📁 Output directory: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='PyQuest Content Generator - Convert CSV files to challenges and lessons',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate challenges
  python content_generator.py challenges examples/challenges.csv

  # Generate lessons
  python content_generator.py lessons examples/lessons.csv

  # Generate both
  python content_generator.py both examples/challenges.csv examples/lessons.csv

  # Specify output directory
  python content_generator.py challenges examples/challenges.csv -o output/
        """
    )

    parser.add_argument(
        'mode',
        choices=['challenges', 'lessons', 'both'],
        help='Type of content to generate'
    )

    parser.add_argument(
        'files',
        nargs='+',
        help='CSV file(s) to process'
    )

    parser.add_argument(
        '-o', '--output',
        default='generated',
        help='Output directory (default: generated/)'
    )

    args = parser.parse_args()

    output_dir = Path(args.output)

    if args.mode == 'challenges':
        if len(args.files) != 1:
            print("❌ Error: challenges mode requires exactly one CSV file")
            sys.exit(1)
        process_challenges(Path(args.files[0]), output_dir)

    elif args.mode == 'lessons':
        if len(args.files) != 1:
            print("❌ Error: lessons mode requires exactly one CSV file")
            sys.exit(1)
        process_lessons(Path(args.files[0]), output_dir)

    elif args.mode == 'both':
        if len(args.files) != 2:
            print("❌ Error: both mode requires exactly two CSV files (challenges, lessons)")
            sys.exit(1)
        process_challenges(Path(args.files[0]), output_dir)
        process_lessons(Path(args.files[1]), output_dir)


if __name__ == '__main__':
    main()

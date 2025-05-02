import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.syllabus import SyllabusHelper

# Set API key directly for testing
OPENROUTER_API = "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"  # Replace with your actual API key

# Fake data classes
class FakeStudent:
    def __init__(self):
        self.goals = "Improve math skills"
        self.current_grades = "B"
        self.weak_areas = "Algebra"
        self.language = "English"
        self.country = "USA"
        self.personality = "Curious"
        self.interests = "Puzzles"
        self.hobbies = "Chess"

class FakeSection:
    def __init__(self):
        self.theme = "Mathematics"
        self.number_of_lessons = 10
        self.length_of_session = 60
        self.subject = "Math"
        self.frameworks = "Singapore Math"
        self.goals = "Master algebra and geometry"
        self.level = "Intermediate"
        self.student_characteristics = "Highly motivated"
        self.students = self

    def all(self):
        return [FakeStudent()]

class TestSyllabusHelper(unittest.TestCase):
    def setUp(self):
        # Create helper with direct API key
        self.helper = SyllabusHelper()
        self.helper.api_key = OPENROUTER_API  # Set API key directly
        self.section = FakeSection()

    def test_generate_returns_non_empty_response(self):
        """Test that the generate method returns a non-empty response"""
        result = self.helper.generate(self.section)
        self.assertIsNotNone(result)
        self.assertNotEqual(result.strip(), "")
        print("\n=== Generated Response ===")
        print(result)

    def test_generate_includes_required_sections(self):
        """Test that the response includes key curriculum sections"""
        result = self.helper.generate(self.section)
        required_keywords = [
            "Learning Objectives",
            "Session",
            "Topics",
            "Skills",
            "Concepts"
        ]
        for keyword in required_keywords:
            self.assertIn(keyword, result, f"Response should contain '{keyword}'")

    def test_generate_personalizes_content(self):
        """Test that the response includes personalized content based on student info"""
        result = self.helper.generate(self.section)
        student_specific_info = [
            "Math",
            "Algebra",
            "Intermediate",
            "Singapore Math"
        ]
        for info in student_specific_info:
            self.assertIn(info, result, f"Response should contain personalized info '{info}'")

    def test_generate_with_empty_section(self):
        """Test handling of empty section data"""
        empty_section = FakeSection()
        empty_section.theme = ""
        empty_section.goals = ""
        result = self.helper.generate(empty_section)
        self.assertIsNotNone(result)
        print("\n=== Response for Empty Section ===")
        print(result)

    def test_generate_response_format(self):
        """Test that the response follows expected format"""
        result = self.helper.generate(self.section)
        # Check if response contains session numbers
        for i in range(1, self.section.number_of_lessons + 1):
            self.assertIn(f"Session {i}", result, f"Response should contain 'Session {i}'")

if __name__ == "__main__":
    # Run all tests
    unittest.main(argv=[''], verbosity=2, exit=False)
from .AI import AI

class LessonPlanHelper(AI):

    def generate(self, section, session_number, syllabus_content):
        """
        Generate a detailed lesson plan for a specific session.
        
        Args:
            section: The section object containing course and student information
            session_number: The session number to generate a plan for
            syllabus_content: The content of the syllabus to ensure consistency
        """
        prompt = f"""
You are an expert teacher and lesson planner. You are creating a lesson plan for neurodivergent students (ADHD, Autism, Dyslexia, Dyspraxia, etc.)

Please create a detailed lesson plan for Session {session_number} of the following course:

Subject: {section.theme}
Session Length: {section.length_of_session} minutes
Level: {section.level}

Here is the student's information:
"""

        for i, student in enumerate(section.students.all(), start=1):
            prompt += f"""
Student {i}:
- Goal & Expectations: {student.goals or "Not provided"}
- Current Grade/Level: {student.current_grades or "Not provided"}
- Weak Areas: {student.weak_areas or "Not provided"}
- Language: {student.language or "Unknown"}
- Country: {student.country or "Unknown"}
- Personality: {student.personality or "Not provided"}
- Interests: {student.interests or "Not provided"}
- Hobbies: {student.hobbies or "Not provided"}
"""

        prompt += f"""
Here is the course syllabus for reference:
{syllabus_content}

### Your Task:

Create a detailed lesson plan for Session {session_number} that includes:

1. Timeline Breakdown (in minutes):
   - Warm-up and Review (5-10 minutes)
   - Main Activities (with specific time allocations)
   - Practice/Application
   - Summary and Next Steps

2. Warm-up Questions:
   - 3-5 engaging questions to activate prior knowledge
   - Questions should connect to previous sessions
   - Include questions that assess understanding of prerequisites

3. Detailed Activities:
   - List all activities in sequence
   - For each activity:
     * Clear instructions
     * Required materials
     * Expected outcomes
     * Assessment criteria
     * Differentiation strategies for different learning styles

4. Practice Exercises:
   - Guided practice problems/activities
   - Independent practice opportunities
   - Real-world applications

5. Assessment Methods:
   - How to check understanding during the lesson
   - Exit ticket or closing assessment
   - Homework or follow-up activities

6. Materials Needed:
   - List all required materials
   - Any handouts or resources
   - Technology requirements

7. Differentiation Strategies:
   - How to support struggling students
   - How to challenge advanced students
   - Accommodations for different learning styles

8. Closing:
   - Summary of key points
   - Preview of next session
   - Assignment of any homework

### Constraints:

- Ensure alignment with the overall syllabus
- Make activities engaging and interactive
- Include clear time allocations
- Provide specific examples and practice problems
- Consider the student's learning style and preferences
- Include assessment opportunities
- Make it practical and age-appropriate
- Ensure smooth transitions between activities
"""

        response = self.ask(prompt)

        # Validate response and ensure correct output format
        if response:
            return response
        return None  # Return None if response is invalid 

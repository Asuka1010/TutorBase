#from rag.pipeline import RAGPipeline
from django.conf import settings
from .AI import AI


class SyllabusHelper(AI):
    # def __init__(self):
    #     # rag/pipeline의 RAGPipeline 사용
    #     self.pipeline = RAGPipeline(
    #         vector_db_path="rag/vectorDB/faiss_index.index",
    #         docs_path="rag/vectorDB/metadata.pkl",
    #         reranker_model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
    #         openai_api_key=settings.OPENROUTER_API
    #     )

    def generate(self, section):
        """
        Generate a personalized curriculum syllabus for student.

        Args:
            section: The section object containing course and student information.

        Returns:
            str or None: Generated syllabus text, or None if generation failed.
        """
        prompt = f"""
You are an expert teacher and curriculum designer. You are creating a personalized curriculum syllabus for neurodivergent students (ADHD, Autism, Dyslexia, Dyspraxia, etc.)

Please create a personalized curriculum syllabus for teaching on the subject of:  
{section.theme}

- Number of Sessions:  {section.number_of_lessons}  
- Session Length:  {section.length_of_session} minutes
- Subject/Discipline: {section.subject}
- Frameworks to include: {section.frameworks}
- Goals for the course: {section.goals}
- Level: {section.level}
- Student Characteristics: {section.student_characteristics}

Here is the student's information:
"""
        for i, student in enumerate(section.students.all(), start=1):
            prompt += f"""
Student {i}:
- Goal & Expectations for Students:  {student.goals or "Not provided"}
- Current Grade/Level in Subject:  {student.current_grades or "Not provided"}
- Identified Weak Areas:  {student.weak_areas or "Not provided"}
- Student Demographics (age, language, personality):  
  - Language: {student.language or "Unknown"}
  - Country: {student.country or "Unknown"}
  - Personality: {student.personality or "Not provided"}
- Student Interests and Hobbies:  {student.interests or "Not provided"}, {student.hobbies or "Not provided"}
"""

        prompt += """
### Your Task:

1. Analyze the weak areas and break them down into key sub-skills or components.  
2. Generate SMART Learning Objectives for each sub-skill.
3. Structure a long-term curriculum across the teaching period into a overall roadmap, with clear themes or focus areas.  
   *(e.g., Session 1: Vocabulary Mastery)*
4. For each session:
   - Provide a breakdown of topics
   - Outline core strategies and skills
   - List the KEY CONCEPTS to cover

### Constraints:
- Personalize to the student's background and level.
- Prioritize remediation of weak areas before advancing to broader objectives.
- Ensure logical skill progression.
- Assume no prior knowledge unless stated.
- Make it practical and age-appropriate.
"""

        #response = self.pipeline.run(prompt)
        response = self.ask(prompt)

        # Validate response and ensure correct output format
        if response:
            return response
        return None  # Return None if response is invalid

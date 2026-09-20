"""
GradePilot - Python FastAPI AI & Parsing Service
Handles Syllabus Document Parsing & LLM Note/Diagram Generation via BYOK (Bring-Your-Own-Key).
"""

import os
import json
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, Status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai

app = FastAPI(
    title="GradePilot AI Engine",
    description="Python microservice for syllabus parsing and structured LLM note/diagram generation.",
    version="1.0.0"
)

# Enable CORS for local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class SyllabusParseRequest(BaseModel):
    course_title: str = Field(..., example="CS301 - Data Structures")
    syllabus_text: str = Field(..., example="Week 1: Big O Notation\nWeek 2: Linked Lists")

class TopicItem(BaseModel):
    week: int
    title: str

class SyllabusParseResponse(BaseModel):
    course_code: str
    course_title: str
    topics: List[TopicItem]

class GenerateNoteRequest(BaseModel):
    course_title: str
    topic_title: str

class FlashcardItem(BaseModel):
    front: str
    back: str

class QuizQuestionItem(BaseModel):
    id: str
    type: str  # 'mcq', 'true_false', 'short'
    question: str
    options: Optional[List[str]] = None
    correctIndex: Optional[int] = None
    keywords: Optional[List[str]] = None

class GeneratedNoteResponse(BaseModel):
    title: str
    concepts: str
    analogy: str
    bullets: List[str]
    mermaidSyntax: str
    flashcards: List[FlashcardItem]
    quiz: List[QuizQuestionItem]

# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "GradePilot FastAPI AI Service"}

@app.post("/api/ai/parse-syllabus", response_model=SyllabusParseResponse)
def parse_syllabus(req: SyllabusParseRequest):
    """
    Parses unstructured text syllabus into week-by-week topic items.
    """
    lines = [line.strip() for line in req.syllabus_text.split("\n") if line.strip()]
    topics: List[TopicItem] = []
    
    week_counter = 1
    for line in lines:
        if ":" in line:
            title = line.split(":", 1)[1].strip()
        else:
            title = line
        
        topics.append(TopicItem(week=week_counter, title=title))
        week_counter += 1

    return SyllabusParseResponse(
        course_code=req.course_title.split("-")[0].strip() if "-" in req.course_title else "COURSE",
        course_title=req.course_title,
        topics=topics
    )

@app.post("/api/ai/generate-notes", response_model=GeneratedNoteResponse)
def generate_notes(
    req: GenerateNoteRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Generates structured study notes, Mermaid flowchart syntax, flashcards, and quizzes using BYOK Gemini key.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=Status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header. Please provide your Google Gemini API key via BYOK settings."
        )

    try:
        # Configure Gemini API with client-provided key
        genai.configure(api_key=x_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        Act as an elite computer science professor and educational tutor.
        Generate structured study material for Course: "{req.course_title}", Topic: "{req.topic_title}".
        
        Respond STRICTLY in valid raw JSON with NO markdown code block formatting (no ```json).
        The JSON must strictly match this schema:
        {{
          "title": "{req.topic_title}",
          "concepts": "A 2-3 sentence clear explanation of the core technical concept.",
          "analogy": "A memorable real-world analogy explaining the concept.",
          "bullets": [
            "Key takeaway point 1",
            "Key takeaway point 2",
            "Key takeaway point 3"
          ],
          "mermaidSyntax": "graph TD\\n  A[Start] --> B[Process]\\n  B --> C[Result]",
          "flashcards": [
            {{"front": "Question 1?", "back": "Answer 1"}},
            {{"front": "Question 2?", "back": "Answer 2"}}
          ],
          "quiz": [
            {{
              "id": "q1",
              "type": "mcq",
              "question": "Sample multiple choice question?",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "correctIndex": 0
            }},
            {{
              "id": "q2",
              "type": "true_false",
              "question": "Sample true/false question statement.",
              "options": ["True", "False"],
              "correctIndex": 0
            }},
            {{
              "id": "q3",
              "type": "short",
              "question": "Sample short answer prompt?",
              "keywords": ["keyword1", "keyword2"]
            }}
          ]
        }}
        """

        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Clean potential markdown fences if returned
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        
        data = json.loads(raw_text.strip())
        return GeneratedNoteResponse(**data)

    except Exception as e:
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM Generation Error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

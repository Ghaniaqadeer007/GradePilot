-- ============================================================================
-- GradePilot Relational Database Schema (PostgreSQL / Supabase)
-- Zero-Cost Central Caching Architecture
-- ============================================================================

-- Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    semester VARCHAR(50) DEFAULT 'Fall 2026',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Topics Table
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    week_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_course_week UNIQUE (course_id, week_number)
);

-- 3. Central Cached Notes Table (Zero-Cost LLM Cache)
CREATE TABLE IF NOT EXISTS cached_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID UNIQUE NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    content_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Flashcards Table (Backup / Sync for Client SM-2 Data)
CREATE TABLE IF NOT EXISTS flashcards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    easiness_factor NUMERIC(4, 2) DEFAULT 2.50,
    interval_days INT DEFAULT 1,
    repetitions INT DEFAULT 0,
    next_due_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Semester Calendar & Deadlines Table
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('exam', 'quiz', 'project', 'lecture')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_topics_course ON topics(course_id);
CREATE INDEX IF NOT EXISTS idx_cached_notes_topic ON cached_notes(topic_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_topic ON flashcards(topic_id);
CREATE INDEX IF NOT EXISTS idx_calendar_date ON calendar_events(event_date);

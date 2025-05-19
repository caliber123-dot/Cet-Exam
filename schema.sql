"""
PostgreSQL table creation script for CET Exam App
"""

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(255) UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    text TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    explanation TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Options Table
CREATE TABLE IF NOT EXISTS options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    option_id VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (question_id, option_id)
);

-- Exams Table
CREATE TABLE IF NOT EXISTS exams (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(255) UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Exam Categories Table
CREATE TABLE IF NOT EXISTS exam_categories (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    UNIQUE (exam_id, category)
);

-- Exam Questions Table
CREATE TABLE IF NOT EXISTS exam_questions (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    question_order INTEGER NOT NULL,
    UNIQUE (exam_id, question_id)
);

-- Exam Results Table
CREATE TABLE IF NOT EXISTS exam_results (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(255) UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    score FLOAT NOT NULL,
    max_score FLOAT NOT NULL,
    completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Result Answers Table
CREATE TABLE IF NOT EXISTS result_answers (
    id SERIAL PRIMARY KEY,
    result_id INTEGER NOT NULL REFERENCES exam_results(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    selected_option_id VARCHAR(50),
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (result_id, question_id)
);

-- Category Scores Table
CREATE TABLE IF NOT EXISTS category_scores (
    id SERIAL PRIMARY KEY,
    result_id INTEGER NOT NULL REFERENCES exam_results(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    UNIQUE (result_id, category)
);

-- Recommendations Table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    result_id INTEGER NOT NULL REFERENCES exam_results(id) ON DELETE CASCADE,
    category VARCHAR(50),
    recommendation_text TEXT NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS idx_exams_is_active ON exams(is_active);
CREATE INDEX IF NOT EXISTS idx_exam_results_user_id ON exam_results(user_id);
CREATE INDEX IF NOT EXISTS idx_result_answers_result_id ON result_answers(result_id);
CREATE INDEX IF NOT EXISTS idx_category_scores_result_id ON category_scores(result_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_result_id ON recommendations(result_id);

// Theme toggle functionality for CET Exam App
document.addEventListener('DOMContentLoaded', function() {
    // Get the theme toggle checkbox
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check for saved theme preference or use default
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the saved theme or default
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Update checkbox state based on current theme
    if (currentTheme === 'dark') {
        themeToggle.checked = true;
        updateThemeIcon('dark');
    } else {
        updateThemeIcon('light');
    }
    
    // Listen for toggle changes
    themeToggle.addEventListener('change', function(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            updateThemeIcon('dark');
            document.body.classList.add('fade-transition');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            updateThemeIcon('light');
            document.body.classList.add('fade-transition');
        }
        
        // Remove transition class after animation completes
        setTimeout(() => {
            document.body.classList.remove('fade-transition');
        }, 500);
    });
    
    // Update theme icon based on current theme
    function updateThemeIcon(theme) {
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.innerHTML = '🌙';
                themeIcon.setAttribute('title', 'Switch to Light Mode');
            } else {
                themeIcon.innerHTML = '☀️';
                themeIcon.setAttribute('title', 'Switch to Dark Mode');
            }
        }
    }
});

// Authentication service for CET Exam App
class AuthService {
    constructor() {
        this.apiUrl = '/api/auth';
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
    }
    
    async login(email, password) {
        try {
            const response = await fetch(`${this.apiUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            // Check if response is ok before trying to parse JSON
            if (!response.ok) {
                // Check content type to handle appropriately
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `Login failed with status: ${response.status}`);
                } else {
                    // Handle non-JSON error responses
                    throw new Error(`Login failed with status: ${response.status}`);
                }
            }
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            
            this.token = data.token;
            this.user = data.user;
            
            localStorage.setItem('token', this.token);
            localStorage.setItem('user', JSON.stringify(this.user));
            
            return this.user;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }
    
    async register(email, password, displayName, role = 'student') {
        try {
            const response = await fetch(`${this.apiUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password, displayName, role })
            });
            
            // Check if response is ok before trying to parse JSON
            if (!response.ok) {
                // Check content type to handle appropriately
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `Registration failed with status: ${response.status}`);
                } else {
                    // Handle non-JSON error responses
                    throw new Error(`Registration failed with status: ${response.status}`);
                }
            }
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }
    
    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login.html';
    }
    
    isAuthenticated() {
        return !!this.token;
    }
    
    isAdmin() {
        return this.user && this.user.role === 'admin';
    }
    
    getToken() {
        return this.token;
    }
    
    getUser() {
        return this.user;
    }
    
    async getAuthenticatedRequest(url, options = {}) {
        if (!this.token) {
            throw new Error('No authentication token available');
        }
        
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${this.token}`
        };
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            // Check if response is ok before trying to parse JSON
            if (!response.ok) {
                // Check content type to handle appropriately
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `Request failed with status: ${response.status}`);
                } else {
                    // Handle non-JSON error responses
                    throw new Error(`Request failed with status: ${response.status}`);
                }
            }
            
            return response;
        } catch (error) {
            console.error('Request error:', error);
            throw error;
        }
    }
}

// Exam service for handling exam-related operations
class ExamService {
    constructor() {
        this.apiUrl = '/api/exam';
        this.authService = new AuthService();
    }
    
    async getExams(activeOnly = true) {
        try {
            const response = await this.authService.getAuthenticatedRequest(
                `${this.apiUrl}/exams?active_only=${activeOnly}`
            );
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data.exams;
        } catch (error) {
            console.error('Error fetching exams:', error);
            throw error;
        }
    }
    
    async getExam(examId, includeQuestions = true) {
        try {
            const response = await this.authService.getAuthenticatedRequest(
                `${this.apiUrl}/exams/${examId}?include_questions=${includeQuestions}`
            );
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data.exam;
        } catch (error) {
            console.error('Error fetching exam:', error);
            throw error;
        }
    }
    
    async createExam(title, description, durationMinutes, questionIds, categories) {
        try {
            const response = await this.authService.getAuthenticatedRequest(
                `${this.apiUrl}/exams`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        title,
                        description,
                        duration_minutes: durationMinutes,
                        questions: questionIds, // Changed from question_ids to questions to match backend expectation
                        categories
                    })
                }
            );
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data.exam;
        } catch (error) {
            console.error('Error creating exam:', error);
            throw error;
        }
    }
    
    async createQuestion(text, category, options, explanation, difficultyLevel = 2) {
        try {
            const response = await this.authService.getAuthenticatedRequest(
                `${this.apiUrl}/questions`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text,
                        category,
                        options,
                        explanation,
                        difficulty_level: difficultyLevel
                    })
                }
            );
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data.question;
        } catch (error) {
            console.error('Error creating question:', error);
            throw error;
        }
    }
    
    async getQuestionsByCategories(categories) {
        try {
            // Convert categories array to comma-separated string
            const categoriesParam = categories.join(',');
            
            const response = await this.authService.getAuthenticatedRequest(
                `${this.apiUrl}/questions?categories=${categoriesParam}`
            );
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data.questions;
        } catch (error) {
            console.error('Error fetching questions by categories:', error);
            throw error;
        }
    }
    
    async submitExam(examId, answers) {
        try {
            const response = await this.authService.getAuthenticatedRequest(
                `${this.apiUrl}/exams/${examId}/submit`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ answers })
                }
            );
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error submitting exam:', error);
            throw error;
        }
    }
    
    async getResult(resultId) {
        try {
            const response = await this.authService.getAuthenticatedRequest(
                `${this.apiUrl}/results/${resultId}`
            );
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data.result;
        } catch (error) {
            console.error('Error fetching result:', error);
            throw error;
        }
    }
    
    async getUserResults(userId) {
        try {
            const response = await this.authService.getAuthenticatedRequest(
                `${this.apiUrl}/users/${userId}/results`
            );
            
            // Safe to parse JSON for successful responses
            const data = await response.json();
            return data.results;
        } catch (error) {
            console.error('Error fetching user results:', error);
            throw error;
        }
    }
}

// Certificate generator
class CertificateGenerator {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
    }
    
    async generateCertificate(userData, examData, resultData) {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set background
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw border
        this.ctx.strokeStyle = '#4a6da7';
        this.ctx.lineWidth = 15;
        this.ctx.strokeRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw header
        this.ctx.fillStyle = '#4a6da7';
        this.ctx.font = 'bold 40px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Certificate of Completion', this.canvas.width / 2, 100);
        
        // Draw content
        this.ctx.fillStyle = '#212529';
        this.ctx.font = '24px Arial';
        this.ctx.fillText('This is to certify that', this.canvas.width / 2, 180);
        
        // Draw name
        this.ctx.font = 'bold 36px Arial';
        this.ctx.fillText(userData.displayName, this.canvas.width / 2, 240);
        
        // Draw exam details
        this.ctx.font = '24px Arial';
        this.ctx.fillText(`has successfully completed the exam`, this.canvas.width / 2, 300);
        this.ctx.font = 'bold 30px Arial';
        this.ctx.fillText(examData.title, this.canvas.width / 2, 350);
        
        // Draw score
        this.ctx.font = '24px Arial';
        this.ctx.fillText(`with a score of`, this.canvas.width / 2, 410);
        this.ctx.font = 'bold 36px Arial';
        this.ctx.fillText(`${Math.round(resultData.score)}%`, this.canvas.width / 2, 460);
        
        // Draw date
        const date = new Date(resultData.completed_at);
        this.ctx.font = '20px Arial';
        this.ctx.fillText(`Date: ${date.toLocaleDateString()}`, this.canvas.width / 2, 520);
        
        // Draw signature line
        this.ctx.beginPath();
        this.ctx.moveTo(this.canvas.width / 2 - 100, 600);
        this.ctx.lineTo(this.canvas.width / 2 + 100, 600);
        this.ctx.stroke();
        
        this.ctx.font = '20px Arial';
        this.ctx.fillText('Authorized Signature', this.canvas.width / 2, 630);
        
        return this.canvas.toDataURL('image/png');
    }
    
    downloadCertificate(dataUrl, filename = 'certificate.png') {
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = filename;
        link.click();
    }
}

# 🎴 Asha AI
An interactive chat interface designed to empower women in their professional journeys.
Made for: JobsForHer Foundation 

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0.1-lightgrey.svg)
![Bootstrap](https://img.shields.io/badge/bootstrap-5.0.2-purple.svg)
![JavaScript](https://img.shields.io/badge/javascript-ES6+-yellow.svg)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-1.4.23-red.svg)
![HTML5](https://img.shields.io/badge/html-5-orange.svg)
![CSS3](https://img.shields.io/badge/css-3-blue.svg)
![RegEx](https://img.shields.io/badge/regex-100+_patterns-brightgreen.svg)
![AJAX](https://img.shields.io/badge/ajax-asynchronous-blueviolet.svg)
![Jinja2](https://img.shields.io/badge/jinja-3.0.1-red.svg)
![Werkzeug](https://img.shields.io/badge/werkzeug-2.0.1-blue.svg)
![pytest](https://img.shields.io/badge/pytest-6.2.5-green.svg)
![JSON](https://img.shields.io/badge/json-structured_data-brightgreen.svg)
![Fetch API](https://img.shields.io/badge/fetch_api-native-orange.svg)



## [✨] : What It Does

It helps users discover career opportunities, professional development resources, and networking events specifically focused on women's advancement in the workplace. 
The assistant processes natural language queries to provide relevant information and guidance tailored to women's career needs.

## [🎯] : Key Features
<br>
<details>
<br><br><summary> <b>[🗃️] :Click to preview features </b> </summary> 
<br>
<b>Initial page:</b>
<br>
<img width ="500" src="https://github.com/user-attachments/assets/c8a3b562-aec6-4585-b8d2-4afc0c7634c2" alt="/info"/>
<br><br>
<b>Job Search</b>
<br>
<img width="500" src="https://github.com/user-attachments/assets/0ee0247a-4df4-46db-91c0-58987666f4a4" alt="/store"/>
<br><br>
<b>Hallucination Handling</b>
<br>
<img width="500" src="https://github.com/user-attachments/assets/b8f10ff9-d70e-48f7-93e4-63393abc3a89" alt="/queue"/>
  
<hr>
</details>
<br>

- **Engaging Welcome Experience**: Greets users with friendly messages and random virtual treats to create a warm, approachable atmosphere
- **Natural Language Job Search**: Finds relevant career opportunities using sophisticated regex keyword extraction
- **Comprehensive Filtering**: Filters results by job type, location, industry, and skill level
- **RAG-based Information Retrieval**: Uses Retrieval Augmented Generation through regex keyword matching for relevant information
- **Advanced Bias Detection**: Uses over 100 regex patterns to detect and prevent any form of toxicity, gender bias, stereotypes, and inappropriate language
- **Guardrails Implementation**: Redirects off-topic queries back to career-focused conversations
- **Inspirational Quotes**: Displays random motivational quotes from women leaders during each session
- **Privacy Protection**: Sessions are anonymized and automatically deleted after 30 minutes of inactivity
- **Interactive Feedback**: Users can provide thumbs up/down feedback on responses
- **Light/Dark Mode Toggle**: Adjustable interface for comfortable viewing
- **Responsive Design**: Works seamlessly across mobile and desktop devices
- **In-Chat Registration**: Complete user registration process directly within the chat interface
- **Form Handling**: In-chat registration and application forms with validation for new users and job applications
- **HerKey Brand Integration**: Uses HerKey's component colors and design language for visual consistency
- **Self-Care Reminders**: Provides periodic wellness and self-care reminders to promote work-life balance



## [🚀] : How to Use
visit the link in the repo (https://jobsforher-chatbot-production.up.railway.app/)

## [🔧] : Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** 
| Web Framework | Flask | Handles HTTP requests, routing, and API endpoints |
| Database | SQL (SQLAlchemy) | Stores user interactions, feedback, and bias scores |
| Session Management | Flask Session | Manages anonymous sessions with 30-min expiration |
| Logging | Python logging | Application monitoring and debugging |
| **Bias Detection System** |  |  |
| Pattern Recognition | Regular Expressions | 100+ patterns for detecting various bias types |
| ML Integration | bias_detector.py | Assigns numerical scores (0-1) to detected bias |
| Multi-Layer Detection | guardrails.py | Six-stage pipeline for content filtering |
| **Frontend** |  |  |
| UI Framework | Bootstrap | Responsive layout and components |
| Interactivity | JavaScript | Client-side chat handling and state management |
| Icons | Font Awesome | UI elements (feedback buttons, theme toggle) |
| Styling | CSS | Custom styling for chat interface |
| **Communication** |  |  |
| API Communication | Fetch API | Asynchronous client-server communication |
| Data Format | JSON | Data exchange between client and server |
| **User Experience** |  |  |
| Theme Toggle | JavaScript/CSS | Light/dark mode functionality |
| Message History | Client-side JS | Maintains chat history during session |
| Typing Indicator | CSS Animation | Shows when bot is "typing" a response |
| Time Display | JavaScript | Shows message timestamps |
| **Content Features** |  |  |
| Welcome Messages | Random selection | Greeting with virtual treats (cookies, flowers) |
| Motivational Quotes | Random selection | Inspirational career quotes |
| Privacy Protection | Automatic cleanup | Session data deleted after 30 minutes |
| **Analytics** |  |  |
| Interaction Tracking | SQL Database | Logs all messages with bias scores |
| Feedback Collection | AJAX/API | Records user thumbs up/down feedback |
| **Information Retrieval** |  |  |
| RAG System | Regex Pattern Matching | Extracts keywords for relevant information retrieval |
| Event Filtering | Python | Filters by type, location, and keywords |
| **Testing** |  |  |
| Unit Testing | pytest | Backend function testing |
| Integration Testing | unittest | Testing API endpoints and workflows |
| **Security** |  |  |
| Input Validation | Server-side checks | Protection against XSS and injection attacks (for future)|
| Form Security | CSRF Protection | Secure form submission handling |
| Authentication | Session tokens | Secure, anonymous session management |

## Future Enhancements
- XSS and SQL injection detection and mitigation
- Advanced RAG (Retrieval-Augmented Generation) with semantic search capabilities
- Integration of sentence transformers model for better query understanding
- AI-powered resume analysis and improvement suggestions
- Integration with virtual interview practice modules
- Expanded mentorship matching with scheduling functionality
- Calendar integration for event scheduling
- Advanced filtering options (date range, cost, skills)
- Social media integration for profile enhancement

## Acknowledgments
![SASS](https://img.shields.io/badge/sass-1.45.0-pink.svg)
![Font Awesome](https://img.shields.io/badge/font_awesome-6.0.0-green.svg)


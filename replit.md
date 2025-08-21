# GROUP6 Survey Application

## Overview

GROUP6 Survey Application is a web-based survey creation and management platform built with Flask. The application enables users to create customizable surveys with multiple question types, collect responses from participants, and manage survey data through an intuitive interface. It provides a complete survey lifecycle from creation to response collection with a focus on simplicity and user experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The frontend uses a traditional server-side rendered approach with Flask's Jinja2 templating engine:

- **Template System**: Modular HTML templates for different survey functionalities (creation, viewing, taking surveys, listing)
- **Responsive Design**: Mobile-first CSS approach with hamburger navigation and flexible layouts
- **Interactive Components**: Vanilla JavaScript for dynamic survey building, form validation, and mobile navigation
- **Static Assets**: Organized CSS and JavaScript files with Font Awesome icons for visual enhancement

### Backend Architecture
The backend follows a Flask-based monolithic architecture:

- **Route Handlers**: RESTful endpoints for survey CRUD operations, response submission, and page rendering
- **Database Layer**: SQLite integration with raw SQL queries for data persistence
- **Session Management**: Flask sessions with configurable secret keys for user state management
- **Template Rendering**: Server-side HTML generation using Jinja2 templates

### Database Design
SQLite database with a normalized relational schema:

- **Surveys Table**: Core survey metadata (title, description, timestamps)
- **Questions Table**: Question details with foreign key relationships, support for different question types, ordering, and requirement flags
- **Responses Table**: Survey response storage with JSON serialization for flexible answer formats
- **Foreign Key Constraints**: Proper referential integrity between surveys and their questions/responses

### Client-Side Features
Dynamic survey building capabilities:

- **Question Management**: Add/remove questions with multiple choice, checkbox, and text input types
- **Form Persistence**: Auto-save functionality using localStorage to prevent data loss
- **Form Validation**: Client-side validation with visual feedback for required fields
- **Mobile Navigation**: Responsive hamburger menu with touch-friendly interactions

### Data Flow Architecture
- **Survey Creation**: Client-side form building → server validation → database storage
- **Response Collection**: Public survey forms → server processing → response storage
- **Data Retrieval**: Database queries → template rendering → client display

## External Dependencies

### Frontend Dependencies
- **Font Awesome 6.4.0**: Icon library for UI elements and visual indicators
- **Modern CSS**: CSS Grid and Flexbox for responsive layouts without external frameworks

### Backend Dependencies
- **Flask**: Web framework for routing, templating, and request handling
- **SQLite3**: Built-in Python database interface for data persistence
- **JSON**: Built-in Python module for response data serialization

### Development Dependencies
- **Python Standard Library**: datetime, os modules for core functionality
- **Browser APIs**: localStorage for client-side data persistence, standard DOM APIs for interactivity

### Infrastructure Requirements
- **SQLite Database**: File-based database storage (surveys.db)
- **Static File Serving**: Flask's built-in static file handling for CSS/JS assets
- **Environment Variables**: SESSION_SECRET for security configuration
# Overview

This is a Flask-based acquisition management system designed for Escola Morvan Figueiredo. The application manages procurement requests, allowing users to create, track, and manage purchase orders through different status stages. The system includes user authentication, file uploads for budget attachments, status tracking, administrative capabilities, and comprehensive PDF reporting functionality with sample data for demonstration.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask**: Core web framework with SQLAlchemy ORM for database operations
- **Database**: SQLite (default) with support for PostgreSQL via DATABASE_URL environment variable
- **Authentication**: Flask-Login for session management with user roles (admin/regular users)
- **Forms**: Flask-WTF for form handling and validation with file upload support

## Database Design
- **User Model**: Handles authentication, roles (admin/regular), and user relationships
- **AcquisitionRequest Model**: Central entity for purchase requests with status workflow
- **Attachment Model**: File storage metadata linked to requests
- **StatusChange Model**: Audit trail for request status modifications

## Status Workflow
The system implements a four-stage procurement workflow:
1. **Orçamento** (Budget) - Initial request with budget collection
2. **Fase de Compra** (Purchase Phase) - Approved for purchasing
3. **A Caminho** (On the Way) - Items shipped/in transit
4. **Finalizado** (Completed) - Request fulfilled

## File Management
- Upload directory: `uploads/` with 16MB file size limit
- Supported formats: PDF, Word documents, Excel files, and images
- Secure filename generation with conflict prevention
- File metadata stored in database with original filenames

## User Interface
- Bootstrap-based responsive design with dark theme
- Portuguese language interface
- Role-based navigation and feature access
- Real-time form validation and file upload feedback

## Security Features
- Password hashing with Werkzeug security utilities
- Session management with configurable secret keys
- File upload validation and secure filename handling
- Role-based access control for administrative functions
- Administrator-only request deletion with confirmation dialogs

## PDF Reporting System
- Individual request PDF generation with complete details, attachments list, and status history
- General system report with statistics, status distribution, and complete request listing
- Professional formatting with proper page layouts and no overlapping content
- Secure download functionality integrated throughout the interface

## Sample Data
- Pre-populated with demonstration users (Ariane Santos, Edilson Costa, Edson Oliveira)
- Example acquisition requests covering various categories (office supplies, IT equipment, cleaning materials, textbooks, sports equipment)
- Complete status transition history showing realistic workflow progression
- Sample data demonstrates all system features and status workflows

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM and migrations
- **Flask-Login**: User session and authentication management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering

## Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme via CDN
- **Font Awesome 6**: Icon library via CDN
- **Custom CSS/JS**: Application-specific styling and interactions

## Database
- **SQLite**: Default database (file-based)
- **PostgreSQL**: Production database option via DATABASE_URL environment variable
- **SQLAlchemy**: ORM with declarative base and relationship management

## Deployment Infrastructure
- **ProxyFix**: Werkzeug middleware for reverse proxy support
- **Environment Variables**: Configuration for database URL and session secrets
- **File System**: Local file storage for uploaded attachments

## Development Tools
- **Python Logging**: Debug-level logging configuration
- **Flask Debug Mode**: Development server with auto-reload
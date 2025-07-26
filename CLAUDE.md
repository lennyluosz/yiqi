# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a WeChat Mini Program (微信小程序) called "一起呦" (Yiqi) - an event booking and social activity platform. The project consists of:

- **Backend**: Django REST API server located in `backend/Yiqi/Yiqi/`
- **Frontend**: WeChat Mini Program located in `front/`

## Backend Architecture

### Django Project Structure
- **Main project**: `backend/Yiqi/Yiqi/Yiqi/` contains settings, URLs, and WSGI configuration
- **Apps**: Located in `backend/Yiqi/Yiqi/apps/`
  - `users/` - User management and authentication
  - `activity/` - Activity/event management
  - `userOperation/` - User operations (collections, sharing, reporting, browsing)
  - `SharingSet/` - Social sharing functionality
  - `messagess/` - Messaging system
- **Third-party packages**: Located in `backend/Yiqi/Yiqi/partyApp/`
  - `xadmin/` - Enhanced Django admin interface
  - `DjangoUeditor/` - Rich text editor integration

### Key Backend Commands
```bash
# Navigate to Django project root
cd backend/Yiqi/Yiqi/

# Install dependencies
pip install -r requirements.txt

# Run Django development server
python manage.py runserver

# Run database migrations
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser

# Collect static files for production
python manage.py collectstatic
```

### Database Configuration
- **Database**: MySQL
- **Cache**: Redis (configured for sessions and caching)
- **Media files**: Stored in `backend/Yiqi/Yiqi/upload/`
- **Static files**: Served from `backend/Yiqi/Yiqi/static/`

### Admin Interface
- Admin URL: `/YiqiAdmin0001shujian/` (uses xadmin instead of default Django admin)

## Frontend Architecture

### WeChat Mini Program Structure
- **Entry point**: `front/app.js` - Global app configuration and user authentication
- **Pages**: Located in `front/pages/` with standard WeChat Mini Program structure
  - `index/` - Main activity listing and search
  - `user/` - User profile and settings
  - `release/` - Activity creation
  - `messages/` - Messaging interface
  - `video/` - Video content
  - `login/` - Authentication
- **Templates**: Reusable components in `front/templates/`
- **Utils**: Helper functions in `front/utils/`
- **API**: API configuration in `front/api/api.js`

### Frontend Development
```bash
# Navigate to frontend directory
cd front/

# Open in WeChat Developer Tools using project.config.json
```

## Configuration Requirements

Based on the README, to set up the project:

1. **WeChat Configuration**: Configure Mini Program ID and SECRET in `sys_info.py`
2. **Backend Settings**: Configure in `backend/Yiqi/Yiqi/Yiqi/settings.py`:
   - `IMAGES_URL` - Image server URL
   - `DATABASES` - MySQL database connection
   - `CACHES` - Redis server configuration
3. **Database**: Import SQL schema from `backend/sql/yiqi.sql`

## Key Features

- Activity/event creation and management
- User registration and authentication via WeChat
- Social features (sharing, collecting, messaging)
- Location-based services with map integration
- Image and file upload functionality
- Real-time messaging system
- Admin panel for content management

## Development Notes

- **Authentication**: Uses WeChat OAuth2 integration with JWT tokens
- **API**: RESTful API using Django REST Framework
- **File uploads**: Handled through Django with custom upload directories
- **Internationalization**: Configured for Chinese (zh-hans) locale
- **Admin**: Uses xadmin for enhanced administrative interface
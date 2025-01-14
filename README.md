# TimeApp

A web-based event management system focused on music and sports subcultures in Croatia and Slovenia. TimeApp serves as both a public event platform and personal calendar solution.

## Features

### Event Management
- Create and manage public/private events
- Recurring event support
- Rich event attributes including:
  - Title and description
  - Date and time (single/multi-day support)
  - Location and venue
  - External event links
  - Tagging system
  
### Advanced Filtering
- Multi-state tag filtering (include/exclude)
- Keyword search
- Attribute-based filtering (location, date, etc.)
- Real-time filter updates without page reload

### User Interactions
- Like events
- Mark attendance
- Add to personal wishlist/calendar
- Share events externally

### Role-Based Access
#### Viewer
- Create/manage private events
- Request public event promotion
- Interact with public events
- Access personal calendar

#### Editor
- All viewer capabilities
- Create/manage public events

#### Admin
- Full system access
- User management
- Event moderation
- Access to analytics dashboard

## Technical Stack
- Backend: Flask
- Frontend: React
- Async database operations
- Mobile-first responsive design

## Security
- Protected routes (authentication required)
- Password hashing
- Role-based access control

## Pages

### Homepage
- Dynamic event filtering
- Asymmetric event card grid
- Real-time interaction updates

### Personal Calendar
- User-specific event collections
- Personal memos
- Event management tools
- Admin dashboard (for admin users)

## Development Guidelines
- Emphasis on code reusability
- Comprehensive error handling
- Logging system for debugging
- Responsive async operations

## Target Users
- Music and sports enthusiasts in Croatia and Slovenia
- Event organizers
- Community members seeking personal calendar solutions

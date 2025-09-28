# Intellicket Unified Admin Interface

**Comprehensive admin dashboard for managing both CSDAIv2 backend and Intellicket frontend from a single unified interface.**

## 🚀 Overview

The Intellicket Unified Admin Interface provides centralized control and monitoring for the entire Intellicket cybersecurity log analysis platform. This single admin application manages both the CSDAIv2 backend (Flask) and Intellicket frontend (Next.js) systems through a modern, responsive web interface.

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Next.js 15.5 with React 19
- **Styling**: Tailwind CSS 4
- **Backend**: Flask admin API integrated with CSDAIv2
- **Database**: SQLite for admin-specific data
- **Real-time**: WebSocket connections for live monitoring
- **TypeScript**: Full type safety throughout

### System Integration
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Admin Frontend    │    │   CSDAIv2 Backend   │    │ Intellicket Frontend│
│   (Next.js :3001)   │───▶│   (Flask :5003)     │───▶│   (Next.js :3000)  │
│                     │    │                     │    │                     │
│ • Dashboard         │    │ • Admin API         │    │ • User Interface    │
│ • System Control    │    │ • Health Monitoring │    │ • Analysis Tools    │
│ • Health Monitor    │    │ • Analyzer Control  │    │ • File Upload       │
│ • Analytics         │    │ • Session Manager   │    │ • Results Display   │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 🎯 Core Features

### 1. **Unified System Dashboard**
- Real-time status of both CSDAIv2 backend and Intellicket frontend
- System health monitoring with visual indicators
- Component status overview (ML, RAG, Database, API)
- Auto-refresh capabilities with configurable intervals

### 2. **File Upload Analytics**
- Total file count and size metrics
- File type distribution analysis
- Analyzer usage statistics
- Upload trends and patterns
- Recent upload activity monitoring

### 3. **Analyzer Management**
- Enable/disable individual analyzers
- Real-time analyzer health monitoring
- Maintenance mode control per analyzer
- Configuration management
- Performance metrics and usage stats

### 4. **System Health Monitoring**
- Comprehensive health checks for all components
- Performance metrics (CPU, memory, response times)
- Automated health alerts and notifications
- Historical performance data
- System diagnostics and troubleshooting

### 5. **Session Management**
- Active session monitoring and control
- Session termination capabilities
- User activity tracking
- Session cleanup and maintenance
- Performance impact analysis

### 6. **Unified Maintenance Mode**
- Coordinated shutdown of both systems
- Graceful maintenance mode with user notifications
- Scheduled maintenance planning
- Service dependency management
- Automated recovery procedures

### 7. **Advanced Monitoring Features**
- System alerts with severity levels
- Performance bottleneck identification
- Error rate monitoring and alerting
- Audit trail for admin actions
- Configuration change tracking

## 📁 Project Structure

```
intellicket-admin/
├── src/
│   ├── api/                    # API integration layer
│   │   └── unified-admin-client.ts
│   ├── hooks/                  # Custom React hooks
│   │   └── useAdminData.ts
│   ├── pages/                  # Page components
│   │   ├── index.tsx          # Main dashboard
│   │   ├── analyzer-management.tsx
│   │   ├── health-monitor.tsx
│   │   ├── analytics.tsx
│   │   └── maintenance.tsx
│   ├── types/                  # TypeScript definitions
│   │   └── admin.ts
│   └── utils/                  # Utility functions
├── public/                     # Static assets
├── package.json               # Dependencies
├── next.config.js             # Next.js configuration
├── tailwind.config.ts         # Tailwind CSS configuration
└── tsconfig.json              # TypeScript configuration

CSDAIv2/admin/                 # Backend admin services
├── unified_admin_routes.py    # Flask admin API routes
├── admin_db.py               # Admin database models
├── health_monitor.py         # System health monitoring
├── analyzer_controller.py    # Analyzer management
└── maintenance_manager.py    # Maintenance mode control
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+ with Flask
- Running CSDAIv2 backend on port 5003
- Running Intellicket frontend on port 3000

### Installation

1. **Install Dependencies**
   ```bash
   cd intellicket-admin
   npm install
   ```

2. **Configure Environment**
   ```bash
   # Set environment variables in next.config.js
   BACKEND_URL=http://localhost:5003
   FRONTEND_URL=http://localhost:3000
   ADMIN_PORT=3001
   ```

3. **Start Admin Interface**
   ```bash
   # Development mode
   npm run dev

   # Production build
   npm run build
   npm start
   ```

4. **Access Admin Dashboard**
   - Open http://localhost:3001
   - Dashboard automatically redirects from root to /dashboard

### Backend Integration

The admin interface requires the CSDAIv2 backend to register admin routes:

```python
# In CSDAIv2/app.py, add:
try:
    from admin.unified_admin_routes import register_admin_routes
    register_admin_routes(app, config)
    print("✅ Admin API routes registered")
except ImportError as e:
    print(f"⚠️ Admin routes not available: {e}")
```

## 🎛️ Admin Features Guide

### Dashboard Overview
The main dashboard provides a comprehensive view of the entire TrendAI system:

- **System Status Cards**: Real-time backend and frontend health
- **Quick Actions Panel**: Common administrative tasks
- **File Statistics**: Upload metrics and trends
- **Active Sessions**: Current user activity monitoring
- **System Alerts**: Critical notifications and warnings
- **Admin Tools**: Navigation to specialized admin functions

### System Control Features

#### Analyzer Management
- **Enable/Disable**: Toggle individual analyzer availability
- **Health Monitoring**: Real-time analyzer performance tracking
- **Configuration**: Dynamic analyzer parameter adjustment
- **Usage Analytics**: Performance metrics and success rates

#### Maintenance Mode
- **Unified Control**: Single toggle for both systems
- **Graceful Shutdown**: Proper service termination sequence
- **User Notifications**: Maintenance page display
- **Scheduled Maintenance**: Plan and automate maintenance windows

#### Session Management
- **Active Monitoring**: Real-time session tracking
- **Force Termination**: Emergency session cleanup
- **Performance Impact**: Resource usage per session
- **Cleanup Automation**: Expired session removal

### Health Monitoring

#### System Health Dashboard
- **Component Status**: Individual service health checks
- **Performance Metrics**: CPU, memory, response time tracking
- **Alert Management**: Automated notifications for issues
- **Historical Data**: Performance trends and analysis

#### Real-time Updates
- **WebSocket Integration**: Live status updates
- **Configurable Intervals**: Adjustable refresh rates
- **Push Notifications**: Critical alert delivery
- **Health Check Automation**: Continuous monitoring

## 🔧 Configuration

### Refresh Intervals
- **System Health**: 30 seconds (configurable: 10s - 5m)
- **File Statistics**: 5 minutes
- **Active Sessions**: 30 seconds
- **System Alerts**: 1 minute

### Admin Database
The admin interface maintains its own SQLite database for:
- Admin action audit trails
- System alert history
- Analyzer status persistence
- Maintenance mode scheduling
- Configuration change tracking

### API Endpoints

#### System Management
- `GET /admin/system/overview` - Complete system status
- `GET /admin/system/health` - Health check results
- `GET /admin/system/metrics` - Performance metrics

#### Analyzer Control
- `GET /admin/analyzers` - List all analyzers
- `POST /admin/analyzers/{id}/enable` - Enable analyzer
- `POST /admin/analyzers/{id}/disable` - Disable analyzer
- `PUT /admin/analyzers/{id}/config` - Update configuration

#### Session Management
- `GET /admin/sessions/active` - Active sessions
- `POST /admin/sessions/{id}/terminate` - Terminate session
- `POST /admin/sessions/cleanup` - Cleanup expired sessions

#### Maintenance Control
- `GET /admin/maintenance/status` - Maintenance mode status
- `POST /admin/maintenance/set` - Set maintenance mode
- `POST /admin/maintenance/schedule` - Schedule maintenance

## 🧪 Development

### Running in Development
```bash
# Start with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

### Testing
```bash
# Backend API testing
curl http://localhost:5003/admin/health

# Frontend testing
curl http://localhost:3001/api/health
```

### Customization

#### Adding New Admin Features
1. Create new page component in `src/pages/`
2. Add corresponding API endpoints in `CSDAIv2/admin/`
3. Update navigation in main dashboard
4. Add type definitions in `src/types/admin.ts`

#### Extending Health Monitoring
1. Add new component check in `unified_admin_routes.py`
2. Update system overview types
3. Add visualization in health monitoring dashboard

## 🔒 Security Considerations

### Access Control
- **No Authentication Required**: As specified, focuses purely on admin workflows
- **Network Security**: Runs on localhost by default
- **API Security**: Input validation and sanitization
- **Database Security**: SQLite with proper error handling

### Admin Actions Audit
- All admin actions are logged with timestamps
- Configuration changes are tracked
- System modifications are recorded
- Audit trail available for compliance

## 📊 Monitoring and Alerting

### System Alerts
- **Critical**: System offline, component failures
- **Warning**: Performance degradation, high resource usage
- **Info**: Maintenance notifications, configuration changes

### Performance Metrics
- **Response Times**: API and page load performance
- **Resource Usage**: CPU, memory, disk utilization
- **Success Rates**: Analyzer performance and reliability
- **User Activity**: Session counts and usage patterns

## 🚀 Future Enhancements

### Planned Features
1. **Advanced Analytics**: Enhanced reporting and data visualization
2. **Configuration Management**: Centralized config file editing
3. **Backup/Recovery**: Automated system backup and restoration
4. **Performance Optimization**: System tuning recommendations
5. **Integration Monitoring**: External service health checks
6. **Mobile Responsive**: Optimized mobile admin interface

### Scalability Considerations
- **Multi-instance Support**: Managing multiple backend instances
- **Load Balancing**: Health monitoring across distributed systems
- **Database Scaling**: Migration to PostgreSQL for larger deployments
- **Microservices**: Breaking admin services into smaller components

## 📋 Requirements Summary

Your original requirements and our implementations:

✅ **File Upload Dashboard** - Real-time file count, sizes, and analytics
✅ **Analyzer Usage Statistics** - Comprehensive usage tracking and metrics  
✅ **Analyzer Enable/Disable** - Individual analyzer control with persistence
✅ **System Health Monitoring** - Complete stack health monitoring
✅ **Backend Shutdown Control** - Coordinated CSDAIv2 maintenance mode
✅ **Frontend Shutdown Control** - Intellicket maintenance page system

**Enhanced Features Added:**
- Unified system overview with real-time updates
- Session management and monitoring
- System alerts and notification system
- Performance metrics and analytics
- Configuration management capabilities
- Audit trail for admin actions
- Automated health checks and diagnostics

The TrendAI Unified Admin Interface provides enterprise-grade administration capabilities while maintaining the modular, scalable architecture you requested. The system is designed for easy future enhancements and maintains complete separation between admin functions and user-facing features.
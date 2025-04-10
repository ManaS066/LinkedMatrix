# LinkedMatrix

LinkedMatrix is a comprehensive platform connecting students, alumni, companies, and universities to facilitate networking, mentorship, and job opportunities in a single unified ecosystem.

## Overview

The LinkedMatrix platform bridges the gap between academia and industry by creating a network where:
- Students can connect with alumni for mentorship and career guidance
- Alumni can give back to their educational institutions by supporting students
- Companies can discover talented candidates
- Universities can strengthen their industry connections and placement records

## Features

### Real-time Chat System
- One-on-one messaging between students and alumni
- Message persistence and history
- Unread message indicators
- Recommended contacts based on university and department

### User Management
- Multi-user role support (Students, Alumni, HODs, Companies, Universities, Super Admins)
- Profile management for all user types
- Verification workflows for new organizations

### University & Department Networks
- University-specific communities
- Department-based matching and recommendations
- Searchable alumni and student directories

### Job Portal Integration
- Companies can post job opportunities
- Students can discover relevant positions
- Application tracking and management

### Project Showcase
- Students can showcase their academic and personal projects
- Companies can view student portfolios

## Technical Stack

- **Backend**: Flask (Python web framework)
- **Database**: MongoDB (NoSQL database)
- **Real-time Communication**: Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript (with templates)
- **Authentication**: Session-based authentication
- **Scheduling**: APScheduler for background tasks

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/linkedmatrix.git
   cd linkedmatrix
   ```

2. Create and activate virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install requirements:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with the following:
   ```
   MONGO_URI=your_mongodb_connection_string
   SECRET_KEY=your_secret_key
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   ```

5. Run the application:
   ```
   python app.py
   ```

## Usage

### For Students
- Register with your university email
- Complete your profile with academic information
- Connect with alumni from your university and department
- Browse job listings and apply for positions
- Showcase your projects and achievements

### For Alumni
- Register and link to your alma mater
- Mentor students by sharing your professional experiences
- Post job opportunities from your current workplace
- Network with fellow alumni

### For Universities
- Approve student and alumni accounts
- Monitor placement statistics
- Showcase university achievements

### For Companies
- Create a company profile
- Post job listings and internship opportunities
- Discover talented students and alumni
- Track applications and candidate pipelines

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this platform
- Universities and companies who provided feedback during development
- The open-source community for the amazing tools and libraries used in this project
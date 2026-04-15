# School Management System - Stakeholder Panels Documentation

## Overview
The School Management System has been configured with **4 distinct user roles**, each with a customized dashboard and panel tailored to their specific needs and responsibilities.

---

## 1. ADMIN (System Administrator)

### Role Description
- Overall system management and oversight
- User management and access control
- System-wide statistics and monitoring
- Financial overview
- Academic oversight

### Admin Dashboard Features

#### Key Statistics Displayed
- **Total Students**: Count of all enrolled students
- **Total Teachers**: Count of teaching staff
- **Total Classes**: Number of school classes
- **Total Subjects**: All subjects offered
- **Total Users**: System-wide user count
- **Total Accountants**: Finance staff members
- **Total Exams**: Conducted/scheduled exams
- **Total Invoices**: Generated fee invoices
- **Recent Exam Results**: Latest exam data

#### Key Sections
1. **System Overview Statistics**
   - Visual cards showing key metrics
   - Student, teacher, and class distribution
   - Exam and invoice counts

2. **Attendance Breakdown**
   - Present/Absent/Late statistics
   - System-wide attendance analysis

3. **Classes Overview**
   - List of all classes with sections
   - Quick links to class management

4. **Recent Students**
   - Latest enrolled students
   - Student information preview
   - Quick access to student profiles

5. **Fee Management**
   - Recent invoices issued
   - Payment status overview
   - Financial health snapshot

6. **Recent Exams**
   - Latest exam schedules
   - Exam details and total marks
   - Academic calendar overview

#### Access URL
- `/dashboard/` (redirects based on role)

---

## 2. TEACHER (Teaching Staff)

### Role Description
- Manage assigned classes
- Track student progress
- Maintain attendance records
- Monitor exam results
- Manage subjects taught

### Teacher Dashboard Features

#### Profile Section
- Full name and contact information
- Qualifications and specialization
- Date of joining
- Edit profile option

#### Key Statistics
- **Classes Managed**: Number of classes assigned
- **Subjects Teaching**: Count of subjects taught
- **Total Students**: Students across all classes
- **Exams**: Exams for their classes

#### Key Sections

1. **Class Management**
   - List of classes managed
   - Class sections
   - Quick access to class details
   - Student management links

2. **Subject Information**
   - All subjects assigned to teach
   - Subject codes and class mappings
   - Subject-wise student lists

3. **Student Attendance Overview**
   - Present/Absent/Late breakdown for students
   - Class-wise attendance analysis
   - Attendance marking interface

4. **Student Progress Tracking**
   - Recent students in their classes
   - Student roll numbers and class assignments
   - Quick access to student records

5. **Exam Management**
   - Recent exams for their classes
   - Exam dates and total marks
   - Links to view and enter exam results
   - Results management interface

6. **Quick Actions**
   - Mark Attendance
   - View Exams
   - View Classes
   - View Students

#### Features Available
- Mark daily attendance
- Enter exam results
- View student performance
- Manage classroom assignments
- Track academic progress

---

## 3. STUDENT (Enrolled Students)

### Role Description
- View personal academic information
- Track attendance
- Monitor exam results
- Check financial obligations
- View class schedule and subjects

### Student Dashboard Features

#### Student Profile Section
- Student name and contact info
- Roll number (unique identifier)
- Assigned class and section
- Guardian information
- Guardian contact number
- Admission date

#### Key Statistics
- **Subjects**: Number of subjects enrolled
- **Exams**: Total exams for their class
- **Results**: Number of exam results received
- **Attendance**: Overall attendance percentage

#### Key Sections

1. **My Subjects**
   - List of all subjects in their class
   - Subject codes and names
   - Teacher assignments
   - Quick access to subject materials

2. **Exam Results (Latest 5)**
   - Recent exam results
   - Marks obtained vs total marks
   - Grade awarded (A+, A, B, C, F)
   - Color-coded grade display
   - Performance tracking

3. **Complete Attendance History**
   - Daily attendance records
   - Status: Present/Absent/Late
   - Teacher notes and remarks
   - Attendance percentage calculation
   - Missing attendance alerts

4. **Financial Dashboard**
   - **Total Due**: Outstanding fees
   - **Total Paid**: Amount already paid
   - **Outstanding Balance**: Pending amount
   - Visual currency display (₹)

5. **Fee Invoice Management**
   - Recent invoices issued
   - Fee type breakdown
   - Invoice status (Pending/Partial/Paid)
   - Due amount tracking
   - Payment history

6. **Quick Links**
   - View Exam Results
   - My Profile
   - Fee Status
   - Class Information

#### Features Available
- View personal academic progress
- Download exam grade cards
- Check financial status
- View attendance certificate
- Access class schedule
- View subject materials
- Print invoices

---

## 4. ACCOUNTANT (Finance/Accounting Staff)

### Role Description
- Manage school finances
- Create and track invoices
- Record fee payments
- Generate financial reports
- Monitor outstanding dues

### Accountant Dashboard Features

#### Financial Summary Cards

1. **Total Due (₹)**: Sum of all invoice amounts
2. **Total Paid (₹)**: Sum of all payments received
3. **Outstanding Balance (₹)**: Remaining dues
4. **Total Revenue (₹)**: Complete revenue collected

#### Invoice Statistics
- **Total Invoices**: Count of all generated invoices
- **Pending**: Unpaid invoices count
- **Partial**: Partially paid invoices count
- **Paid**: Completely paid invoices count

#### Key Sections

1. **Invoice Status Breakdown**
   - Status-wise invoice distribution
   - Count for Paid/Pending/Partial
   - Percentage representation
   - Visual statistics table

2. **Payment Methods Analysis**
   - Payment method categorization
   - Cash payments tracking
   - Bank transfer records
   - Mobile banking transactions
   - Method-wise revenue breakdown

3. **Pending Invoices (Top 10)**
   - Critical list of unpaid invoices
   - Student information
   - Fee structure details
   - Amount due vs. paid
   - Outstanding balance
   - Invoice date
   - Action buttons for invoice management
   - Follow-up tracking

4. **Recent Invoices**
   - Latest 6 generated invoices
   - Student name
   - Invoice amount
   - Current status
   - Quick access to invoice details

5. **Recent Payments**
   - Latest 6 payment records
   - Student information
   - Payment amount
   - Payment method used
   - Transaction date
   - Payment verification status

6. **Quick Actions**
   - Create New Invoice
   - Record Payment
   - View All Payments
   - View All Invoices

#### Features Available
- Create fee invoices
- Generate payment receipts
- Track outstanding dues
- Payment reconciliation
- Financial reports generation
- Revenue analysis
- Student fee summary
- Monthly/quarterly reports
- Export financial data
- Send payment reminders

#### Payment Methods Supported
- Cash
- Bank Transfer
- Mobile Banking

---

## User Role Distribution

| Role | Count | Responsibilities |
|------|-------|-----------------|
| Admin | 1-3 | System management, oversight |
| Teachers | N | Class management, grading |
| Students | N | Learning, attendance |
| Accountants | 1-3 | Financial management |

---

## Dashboard URL Structure

All dashboards are accessible through the main dashboard URL:
```
http://127.0.0.1:8000/dashboard/
```

The system automatically:
1. Authenticates the user
2. Identifies their role
3. Displays the appropriate dashboard template
4. Populates role-specific data

---

## Authentication & Security

- **Login Required**: All dashboards require user login
- **Role-Based Access Control**: Each user sees only their role-specific dashboard
- **Data Isolation**: 
  - Teachers see only their class data
  - Students see only their personal data
  - Accountants see system-wide financial data
  - Admins see all system data

---

## Customization & Future Enhancements

### Potential Enhancements
1. **Admin Dashboard**
   - Real-time analytics
   - System health monitoring
   - User activity logs
   - Backup management

2. **Teacher Dashboard**
   - Lesson planning tools
   - Assignment submission tracking
   - Parent communication portal
   - Performance analytics

3. **Student Dashboard**
   - Study materials library
   - Assignment submission
   - Class schedule/timetable
   - Parent notifications

4. **Accountant Dashboard**
   - Advanced financial reports
   - Income/expense analysis
   - Budget forecasting
   - Tax calculations
   - Multi-year analysis

---

## Template Files Created

1. **core/admin_dashboard.html** - Admin overview panel
2. **core/teacher_dashboard.html** - Teacher management panel
3. **core/student_dashboard.html** - Student personal panel
4. **core/accountant_dashboard.html** - Finance management panel

---

## Views Implementation

Updated **core/views.py** with:
- Role-based template selection
- Role-specific context data gathering
- Four specialized context methods:
  - `_admin_context()` - System-wide statistics
  - `_teacher_context(user)` - Class and student data
  - `_student_context(user)` - Personal academic data
  - `_accountant_context()` - Financial data

---

## Getting Started

### For Admin:
1. Log in with admin credentials
2. Access `/dashboard/` to see system overview
3. Manage users, classes, and overall configuration

### For Teacher:
1. Log in with teacher credentials
2. Access `/dashboard/` to see class information
3. Mark attendance and manage grades
4. Track student progress

### For Student:
1. Log in with student credentials
2. Access `/dashboard/` to see academic progress
3. View attendance and exam results
4. Check fee status and invoices

### For Accountant:
1. Log in with accountant credentials
2. Access `/dashboard/` to see financial overview
3. Create invoices and record payments
4. Generate financial reports

---

## Database Fields Utilized

### User Models
- CustomUser.role (ADMIN, TEACHER, STUDENT, ACCOUNTANT)
- User.first_name, User.last_name
- User.email

### Academic Models
- SchoolClass, StudentProfile, TeacherProfile
- Subject, Exam, ExamResult

### Attendance Models
- Attendance, AttendanceRecord

### Finance Models
- FeeStructure, FeeInvoice, FeePayment

---

**Last Updated**: April 15, 2026
**Status**: Fully Implemented
**Testing**: Ready for production deployment

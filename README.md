# CyberGuard: Enterprise Cybercrime Reporting & Case Management System

CyberGuard is a professional-grade platform designed for citizens, organizations, and law enforcement agencies to report, track, and investigate cybercrimes.

## Key Features

- **Multi-Role Dashboards**: Tailored experiences for Citizens, Investigators, Organization Admins, and System Administrators.
- **Advanced Investigation Workspace**: Investigators can track case history, add internal notes, catalog evidence (files and URLs), and generate structured summaries.
- **Organization Management**: Businesses can register, manage staff with granular roles (Admin, Staff, Viewer), and report data breaches.
- **Smart Notifications**: Real-time alerts for case assignments, status changes, and escalations.
- **Audit & Analytics**: Transparent activity logs and data-driven insights for administrators.

---

## 🏢 Organization & Staff Management

CyberGuard allows organizations to manage their own reporting team through a hierarchical role system.

### How to Add & Manage Staff (Org Admin)

1. **Register as an Organization**: Create an account via the 'Register' page, selecting the 'Organization' option.
2. **Admin Approval**: Your organization must be approved by a System Administrator before you can manage staff.
3. **Access Manage Staff**: Once approved, log in and navigate to the **"Manage Staff"** link in your sidebar.
4. **Invite/Create Staff Member**:
   - Click the **"Add New Staff"** button.
   - Provide the staff member's details (Name, Email, Username, Password).
   - Select their **Organization Role**:
     - **Admin**: Can report crimes and manage other staff members.
     - **Staff**: Can report crimes and view organizational history.
     - **Viewer**: Read-only access to organization reports.
5. **Update/Remove**: From the staff list, you can edit staff profiles or remove them if they leave the organization.

---

## 🕵️ Investigator Workflow

- **Dashboard**: View your assigned workload, performance metrics (SLA), and urgent tasks.
- **Reporting**: Update case status and add findings. Use the **"Internal"** toggle for private notes.
- **Summary**: Generate a professional, printable **Investigation Summary** highlighting all findings and evidence.

---

## 🌐 Installation & Setup

1. **Environment**: Ensure you have Python 3.8+ installed.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Environment Variables**: Create a `.env` file based on the provided template (if any) or configure your Django secret key and database settings.
5. **Run Server**:
   ```bash
   python manage.py runserver
   ```

---

## 🛠 Technology Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL (recommended) / SQLite (development)
- **UI/UX**: Bootstrap 5 with Custom Dark Cybersecurity Theme
- **Icons**: Bootstrap Icons
- **Visuals**: Chart.js for Dashboards

# Alumni Portal

## Project Overview
**Alumni Connect** is a comprehensive platform designed to bridge the gap between current students and alumni. It fosters key interactions through professional networking, job opportunities, and campus events.

### Key Features
*   **Networking Feed**: Share updates, photos, and achievements with the community.
*   **Alumni & Student Directory**: Browse profiles, search by industry or major, and connect with peers.
*   **Job Board**: Alumni can post job openings, and students can apply directly through the portal with resume uploads.
*   **Events Calendar**: Stay updated on reunions, webinars, and networking meetups.
*   **Profile Management**: Update your bio, industry, and upload a profile photo.
*   **Dark Mode**: A modern, high-contrast "Oceanic Night" interface for comfortable viewing.

---

## Technical Details
*   **Framework**: Django 5.2 (Python 3.12+)
*   **Database**: SQLite (Development) / Ready for PostgreSQL
*   **Styling**: Bootstrap 5 with Custom "Oceanic" Theme

---

## Running the Application

### Port Information
The application runs on Port **8000** by default.

### Health Check
To verify the application is running, perform a health check by accessing the root URL:
*   **URL**: `http://localhost:8000/`
*   **Success Criteria**: A `200 OK` response (displays the Login or Dashboard page) indicates the service is healthy.
*   **Kubernetes**: Use `/` for liveness and readiness probes.

### Local Development
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Migrations**:
    ```bash
    cd app
    python manage.py migrate
    ```
3.  **Start Server**:
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

---

## Project Structure
This repository follows a compliance-ready structure for Kubernetes deployment:

*   `app/` - Contains the Django source code (`manage.py`, `portal/`, etc.).
*   `k8s/` - Kubernetes manifests (`deployment.yaml`, `service.yaml`, `ingress.yaml`).
*   `Dockerfile` - Defines the container image (Multi-stage build).
*   `Jenkinsfile` - CI/CD pipeline configuration (Build -> Test -> Deploy).
*   `requirements.txt` - Python dependencies (Root level).

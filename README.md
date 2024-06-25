# Club Management Portal

Welcome to the Club Management Portal! This project is designed to provide an interface for club members to log in, register, manage tickets, and perform various administrative tasks. Below you'll find all the necessary information to set up, run, and contribute to this project.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Workflow](#workflow)
- [Club Rules](#club-rules)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

- User Authentication: Login and Register.
- Manage Club Members: Add and delete members with different access levels.
- Ticket Management: Create, view, and manage tickets.
- Responsive Design: Optimized for both desktop and mobile devices.
- Leaderboard: Display points gained by members.

## Technologies

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (or any other SQL database)
- **Deployment**: Flask development server

## Installation

### Prerequisites

- Python 3.x
- Flask
- Git

### Steps

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/club-management-portal.git
    cd club-management-portal
    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Set environment variables (Linux/MacOS):

    ```sh
    export FLASK_APP=club
    export FLASK_ENV=development
    ```

    For Windows:

    ```sh
    set FLASK_APP=club
    set FLASK_ENV=development
    ```

5. Initialize the database:

    ```sh
    flask init-db
    ```

6. Run the application:

    ```sh
    flask run
    ```

    The app will be available at `http://127.0.0.1:5000/`.

## Usage

- **Home Page**: Provides options to log in or register.
- **Admin Panel**: Accessible to users with administrative privileges to manage members and tickets.
- **Ticket Creation**: Allows users to create new tickets and manage existing ones.

## Workflow

The workflow for managing tickets is as follows:

1. **Request Ticket**: A member requests a ticket.
2. **Approval**: The ticket creator or club creator approves the request.
   - If approved, the ticket status changes to "In Progress".
   - If not approved, the member can withdraw the request.
3. **Mark Review**: Once the task is done, the member marks the ticket for review.
4. **Final Approval**: The ticket creator or club creator approves the completion.
   - If approved, the ticket status changes to "Completed".
   - Points are awarded to the member.

### Flowchart

## Club Rules
### Club Creator:
- Has ultimate decision-making authority.
- Can grant presidential access.
- Can add and delete any member, including presidents.
- Can approve or reject any ticket.
### Presidents:
- Can add members but cannot add other presidents.
- Can delete any member except other presidents and the club creator.
- Can create and manage their own tickets.
- Can approve tickets created by themselves but not by other presidents.
### Members:
- Must log in with a club code.
- Can request tickets.
- Gain points for completing tickets, which are displayed on a leaderboard.
- get promotions
## API Endpoints
- Here is a brief overview of the main API endpoints:

- GET /: Home page.
- POST /login: Login endpoint.
- POST /register: Register endpoint.
- POST /add_member: Add a new club member.
- POST /delete_member: Delete a club member.
- POST /create_ticket: Create a new ticket.
- GET /ticket/<ticket_id>: Get details of a specific ticket.

  

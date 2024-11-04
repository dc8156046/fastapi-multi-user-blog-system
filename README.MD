# Multi-User Blog System

A multi-user blog system built with Python FastAPI, SQLAlchemy, and PostgreSQL, allowing users to create and manage blog posts, comments, and likes.

## Features

- User registration and authentication
- Create, read, update, and delete blog posts
- Comment on posts with support for images
- Like comments and track likes count
- Secure API endpoints with JWT authentication

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **Environment Management**: Dotenv

## Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Setup Environment Variables
Create a .env file in the root directory and add the following variables:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_tutorial
SECRET_KEY=your_secret_key_here
```

## Running the Application
You can run the application using Uvicorn:
```bash
uvicorn main:app --reload

```

### Prerequisites

Make sure you have the following installed:

- Python 3.7+
- PostgreSQL
- pip

### Clone the Repository

```bash
git clone https://github.com/dc815606/fastapi-multi-user-blog-system.git
cd fastapi-multi-user-blog-system

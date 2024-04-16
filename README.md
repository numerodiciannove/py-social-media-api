# Social Media API
The API allows users to perform various social media actions such as user registration and authentication, profile management, post creation and retrieval, following/unfollowing other users, and more.

### Technologies
- Python
- Django
- Django REST Framework
- Postgre SQL
- Swagger documentation

### How to run with Docker
- Docker should be installed
- You can use .env.sample if it needs
- Run `docker-compose up --build`
- Create admin - "docker-compose exec app python manage.py createsuperuser"

### Documentation
- Documentation available via `/api/doc/swagger/`

# Echo-Cloud_Based_Storage_System

A Django-based cloud storage application that allows users to upload, manage, and share files.

## Features

- User authentication and authorization
- File upload and management
- File sharing capabilities
- Email notifications with custom sender name

## Technologies Used

- Django
- SQLite (default database)
- Azure Storage (for file storage)
- Gmail SMTP (for email notifications)

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/codiologies/Echo-Cloud_Based_Storage_System.git
   cd Echo-Cloud_Based_Storage_System
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a .env file with your configuration:
   ```
   AZURE_ACCOUNT_NAME=your_azure_account_name
   AZURE_ACCOUNT_KEY=your_azure_account_key
   AZURE_CONTAINER=your_azure_container
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. Visit http://127.0.0.1:8000/ in your browser

## 📷 Screenshots  
### Homepage  
![Homepage](GitHub%20Resources/home.png)  

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

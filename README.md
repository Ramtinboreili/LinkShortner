# 🚀 LinkShortner 

Shortify is a **powerful and modern URL shortener** built with Django.  
It allows users to **shorten URLs, track analytics, and manage links** through a beautiful and responsive dashboard.

![Shortify Dashboard](https://your-image-url.com/preview.png)

---

## 📉 Features
✅ **Shorten URLs with ease**  
✅ **User authentication for managing personal links**  
✅ **Track the number of clicks for each short URL**  
✅ **Copy the shortened URL with a single click**  
✅ **Download QR Codes in SVG format**  
✅ **Modern and responsive dark UI**  
✅ **Admin panel for managing all users and links**  

---

## 📉 Installation & Setup
### 🔹 1. Clone the Repository
```sh
git clone https://github.com/Ramtinboreili/LinkShortner.git
cd Shortify
```

### 🔹 2. Create a Virtual Environment & Install Dependencies
```sh
python3 -m venv venv
source venv/bin/activate  # Linux & Mac
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 🔹 3. Run Database Migrations
```sh
python manage.py migrate
```

### 🔹 4. Create a Superuser (Optional)
```sh
python manage.py createsuperuser
```
Fill in the required details to create an **admin account**.

---

## 📉 Running the Project
To start the development server, run:
```sh
python manage.py runserver 0.0.0.0:8000
```
Open your browser and visit:
```
http://127.0.0.1:8000/
```

---

## 📉 Project Routes
| **Route**             | **Description** |
|----------------------|----------------|
| `/`                  | Shorten a URL |
| `/dashboard/`        | User's link management dashboard |
| `/login/`            | User login page |
| `/logout/`           | Logout and end session |
| `/<short_code>/`     | Redirects to original URL |
| `/qrcode-svg/<short_code>/` | Download QR code as SVG |

---

## 📉 Technologies Used
🔹 **Django 5** - Backend Framework  
🔹 **SQLite** - Database  
🔹 **HTML, CSS, JavaScript** - Frontend  
🔹 **Bootstrap** - Responsive UI  
🔹 **Gunicorn** - Production server  

---

## 📉 Developed By
🚀 **360 Develop Team**  
📧 **Email:** info@360developteam.com  
🌐 **Website:** [360developteam.com](https://360developteam.com)  

---

### 🎉 **Enjoy using Shortify and contribute to its development!** 🚀🔥

 

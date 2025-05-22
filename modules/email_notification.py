import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template


def send_message(receiver_name, receiver_email, status, book_title):
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    sender_email = "your-email-address"
    from_email = "Libra Lens"
    password = "your-password"

    data = {
        "student_name": receiver_name,
        "email": receiver_email,
        "book_title": book_title
    }

    if status == "yellow":
        template = Template(html_content_yellow)
        rendered_html = template.render(data)
    elif status == "orange":
        template = Template(html_content_orange)
        rendered_html = template.render(data)
    elif status == "red":
        template = Template(html_content_red)
        rendered_html = template.render(data)
    else:
        template = Template(html_content_error)
        rendered_html = template.render(data)

    receiver_email = data['email']

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = receiver_email
    message["Subject"] = "Notification from Libra Lens"
    message.attach(MIMEText(rendered_html, "html"))

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


html_content_yellow = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notification - Book Return</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }
        .email-container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .email-header {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }
        .email-header h1 {
            margin: 0;
            font-size: 24px;
        }
        .email-body {
            padding: 20px;
        }
        .email-body p {
            font-size: 16px;
            line-height: 1.5;
        }
        .email-footer {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #888;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>Reminder: Book Return</h1>
        </div>
        <div class="email-body">
            <p>Dear {{student_name}},</p>
            <p>This is a friendly reminder that you need to return the book <strong>{{book_title}}</strong> in less than <strong>3 days</strong>.</p>
            <p>Please make sure to return the book on time to avoid any late fees.</p>
            <p>If you have any questions or cannot return the book by the due date, please contact us.</p>
            <a href="mailto:guralnikelias390@gmail.com" class="button">Contact Us</a>
        </div>
        <div class="email-footer">
            <p>Best regards,</p>
            <p>Your Library Team</p>
        </div>
    </div>
</body>
</html>

"""


html_content_orange = """ \
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reminder: Book Return Today</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }
        .email-container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .email-header {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }
        .email-header h1 {
            margin: 0;
            font-size: 24px;
        }
        .email-body {
            padding: 20px;
        }
        .email-body p {
            font-size: 16px;
            line-height: 1.5;
        }
        .email-footer {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #888;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #45a049;
        }
        .due-today {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>Reminder: Book Return Today</h1>
        </div>
        <div class="email-body">
            <p>Dear {{student_name}},</p>
            <p>This is a friendly reminder that the book <strong>{{book_title}}</strong> is due for return today.</p>
            <p><span class="due-today">Please make sure to return it today to avoid any late fees.</span></p>
            
            <p>If you have any issues or cannot return the book today, please contact us immediately.</p>
            <a href="mailto:guralnikelias390@gmail.com" class="button">Contact Us</a>
        </div>
        <div class="email-footer">
            <p>Best regards,</p>
            <p>Your Library Team</p>
        </div>
    </div>
</body>
</html>

"""

html_content_red = """ \
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reminder: Book Overdue</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }
        .email-container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .email-header {
            background-color: #FF5733;
            color: white;
            padding: 10px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }
        .email-header h1 {
            margin: 0;
            font-size: 24px;
        }
        .email-body {
            padding: 20px;
        }
        .email-body p {
            font-size: 16px;
            line-height: 1.5;
        }
        .email-footer {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #888;
        }
        .button {
            background-color: #FF5733;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #e84e1a;
        }
        .overdue {
            color: red;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>Reminder: Book Overdue</h1>
        </div>
        <div class="email-body">
            <p>Dear {{student_name}},</p>
            <p>This is a reminder that the book <strong>{{book_title}}</strong> was due for return and is now overdue.</p>
            <p><span class="overdue">Please return the book as soon as possible to avoid further late fees.</span></p>
            
            <p>If you need assistance or if you are unable to return the book immediately, please get in touch with us as soon as possible.</p>
            <a href="mailto:guralnikelias390@gmail.com" class="button">Contact Us</a>
        </div>
        <div class="email-footer">
            <p>Best regards,</p>
            <p>Your Library Team</p>
        </div>
    </div>
</body>
</html>

"""


html_content_error = """ \
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 Error - Email Not Found</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f8f8;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
        }
        .error-box {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0px 2px 15px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 500px;
        }
        h1 {
            font-size: 100px;
            color: #FF5733;
            margin: 0;
        }
        p {
            font-size: 18px;
            color: #555;
        }
        .button {
            background-color: #FF5733;
            color: white;
            padding: 12px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #e84e1a;
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="error-box">
            <h1>404</h1>
            <p>Oops! The email you're looking for could not be found.</p>
            <p>It seems like the email may have been moved or deleted.</p>
        </div>
    </div>

</body>
</html>

"""

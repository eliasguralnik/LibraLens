<br><br>
<div align="center">
  <img src="assets/LibraLens_Logo.png" alt="LibraLens Logo" width="150">
</div>

# <p style="text-align: center;">Libra Lens</p>
## <p style="text-align: center;">Library Management System</p>
<br><br>
A short description of the project and what it does.
<br><br>
### 📖 Description

This project is an intuitive System for multiple clients developed for Librarians. It was developed to maintain the library and help the librarians to manage there tasks, using sockets, SSL/TLS, sklearn and custom tkinter for the interface.

---
### 🚀 Features

- **AI-Powered Book Recommendations**: Automatically suggests books to users based on their borrowing history and similar items not yet available in the catalog.
<br><br>
- **Multi-Client Support**: Enables multiple users (students and librarians) to interact with the system simultaneously, improving collaboration and efficiency.
<br><br>
- **Real-Time Book Status Monitoring**: Uses a traffic light system to display the status of borrowed books (on-time, overdue, etc.), making it easy for librarians and users to track book returns.
<br><br>
- **Automated Reminders for Overdue Books**: Sends automatic email notifications to users when their borrowed books are overdue, helping to ensure timely returns.

---
### ⚙️ Installation

#### Prerequisites
Before running this project, make sure you have Python installed on your system. You can download it from [here](https://www.python.org/).

#### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/your-project.git
cd your-project 
```

#### Step 2: Install the dependencies
Once you have cloned the repository, you need to install the required dependencies.
```bash
pip install -r requirements.txt
```
This command will install all the necessary packages that are listed in requirements.txt, which are required to run the project.

---
### 🛠️ Usage
**Starting the Server and Client**

To begin using the project, you'll need to start both the server and the client. Before doing so, make sure to configure your `config.json` file to match your system settings, such as the IP address and any other necessary configuration options. This ensures that the server and client can communicate properly.
1. **Configure `config.json` for the Server**:
   - Navigate to the `server` directory and open the `config.json` file.
   - Update the IP address, port, and any other required configuration settings to match your network setup or preferences.
   - For example, ensure that the `server_ip` is set to the correct address and that the port is available for the server.
<br><br>
2. **Configure `config.json` for the Client**:
   - Navigate to the `client` directory and open the `config.json` file.
   - Similar to the server, update the IP address, port, and other settings to ensure that the client can connect to the server.
   - Make sure that the `server_ip` in the client’s `config.json` matches the IP address of the server you configured earlier.
<br><br>
3. **Start the Server**:
   - In the terminal, navigate to the `server` directory.
   - Run the following command to start the server:

   ```bash
   python server.py
   ```
   This will initialize the server and make it ready to accept client connections.
<br><br>
4. **Start the Client:**
    - In a separate terminal window, navigate to the client directory.
    - Run the following command to start the client:
   ```bash
   python server.py
   ```
   The client will now attempt to connect to the server using the IP address and port settings you configured in the config.json files.

---
Once both the server and client are running, you should see communication between them, and the project will be fully operational.  
After a successful connection, the graphical user interface (GUI) will automatically open on the client side, allowing you to interact with the system.
<br><br>
If you encounter any issues with the server-client connection, double-check the settings in both config.json files to ensure they match the correct values.


#### Explanation of Changes:
- **Two `config.json` files**: It is now clearly stated that the `config.json` files in both the server and client directories must be configured.
- **Matching IP and ports**: The client must use the same IP address and port settings as the server in its configuration.

---
### 🧑‍💻 Contributing

Contributions are welcome! If you’d like to improve this project or add new features, please follow these steps:

1. **Fork the repository to your own GitHub account.**
<br><br>
2. **Create a new branch for your changes:**  
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes and commit them:**
    ```bash
   git commit -am "Add: Short description of the feature"
   ```
4. **Push your branch to your forked repository:**
    ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request from your branch to the main repository.**

Please ensure that your code is clean, well-structured, and properly documented.  
Every contribution helps us improve — thank you for your support and involvement!

---
### 📄 License

This project is licensed under the **Apache License 2.0**.

You can view the full license details in the [LICENSE](./LICENSE) file located in the root directory of this repository.

---
### 📬 Contact

If you have any questions, suggestions, or just want to connect — feel free to reach out!

- **Name**: Elias Guralnik
- **Email**: [guralnikelias390@gmail.com](mailto:guralnikelias390@gmail.com)  
- **GitHub**: [github.com/dein-github](https://github.com/dein-github)  
- **LinkedIn**: [linkedin.com/in/dein-linkedin](https://linkedin.com/in/dein-linkedin)  

Looking forward to hearing from you!

---

### 📬 Contact

Hi, I'm Elias – a passionate developer always eager to collaborate, share ideas, or dive into tech discussions!   

Feel free to reach out on any of the platforms below:
<br><br>
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:guralnikelias390@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/EliasX55)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/eliasguralnik)
[![Website](https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=About.me&logoColor=white)](https://www.eliasguralnik.tech)

---
### 🔧 Tech Stack

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/150px-Python-logo-notext.svg.png" alt="Python" width="80" />
  <img src="https://styles.redditmedia.com/t5_8tx64t/styles/communityIcon_kbz7e49k7obb1.png" alt="CustomTkinter" width="110" />
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/SQLite370.svg/250px-SQLite370.svg.png" alt="SQLite3" width="200" />
</p>

- **Language:** Python
- **GUI-Frameworks:** Tkinter, customtkinter
- **Databases:** SQLite3

---
### Explanation of key sections:

- **LibraLens - The library management system**
- **[📖 Description](#-description)**: A short overview of your project.
- **[🚀 Features](#-features)**: Lists the key features of your project.
- **[⚙️ Installation](#-installation)**: A step-by-step guide to setting up and starting the project.
- **[🛠️ Usage](#-usage)**: Instructions on how to run and use the project.
- **[🧑‍💻 Contributing](#-contributing)**: How you can contribute.
- **[📄 License](#-license)**: Explanation of the license under which the project is distributed.
- **[📬 Contact](#-contact)**: Your contact details for questions or collaboration.
- **[🔧 Tech Stack](#-tech-stack)**: Technologies and tools used in your project.

---

### 🙌 Final Words

Thanks for checking out LibraLens.
I hope this project adds real value to your work or inspires something new.

If you found it helpful, feel free to leave a comment — it’s appreciated.


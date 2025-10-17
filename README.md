# e-Courts Cause List Downloader

This project is a Streamlit web application that automates the process of downloading cause lists from the Indian e-Courts services website. It provides a user-friendly interface to specify the court details, handles the web scraping, and generates a downloadable PDF of the cause list.

### Features

-   **User-Friendly Interface:** A simple web interface built with Streamlit to guide the user through the process.
-   **Automated Scraping:** Uses Selenium to navigate the e-Courts website, fill in the required details, and handle pop-ups.
-   **CAPTCHA Handling:** Pauses the process to allow the user to solve the CAPTCHA in the browser.
-   **PDF Generation:** Scrapes the cause list table using BeautifulSoup and generates a well-formatted PDF using ReportLab.
-   **Downloadable PDF:** Allows the user to download the generated PDF directly from the web interface.

### Prerequisites

Before you run the application, you need to have Python 3 and the following libraries installed. You will also need Google Chrome and the corresponding ChromeDriver.

1.  **Install Python libraries:**
    ```bash
    pip install streamlit selenium beautifulsoup4 reportlab
    ```

2.  **ChromeDriver:**
    -   Make sure you have Google Chrome installed.
    -   Download the ChromeDriver that matches your Chrome version from the [official site](https://googlechromelabs.github.io/chrome-for-testing/).
    -   Ensure `chromedriver.exe` is in your system's PATH or in the same directory as the `app.py` script.

### How to Run the Application

1.  Open a terminal or command prompt.
2.  Navigate to the directory where `app.py` is located.
3.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
4.  The application will open in your web browser.

### How to Use the Application

1.  **Enter Court Details:**
    -   Fill in the form with the required details: State, District, Court Complex Index, Court Name Index, and Cause List Date.
    -   Click the "Start Process" button.

2.  **Solve CAPTCHA:**
    -   A new Chrome browser window will open.
    -   Solve the CAPTCHA in the browser window.
    -   Go back to the Streamlit application and click the "Continue after CAPTCHA" button.

3.  **Select Case Type:**
    -   Choose between "Criminal" and "Civil" cases.
    -   Click the "Generate PDF" button.

4.  **Download PDF:**
    -   Once the PDF is generated, a "Download Cause List PDF" button will appear.
    -   Click the button to download the PDF file.

5.  **Start Over:**
    -   To start the process again, click the "Start Over" button.

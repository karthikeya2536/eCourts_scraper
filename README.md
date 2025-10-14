# e-Courts Cause List Scraper

This Python script automates the process of scraping cause list data from the Indian e-Courts services website. It uses Selenium to navigate the website, select specific court details, and extract the cause list table for a given date. The scraped data is then formatted and saved as a professional-looking PDF document using ReportLab.

### Features

-   Automated navigation through State, District, and Court Complex dropdowns.
-   Dynamic selection of the first available court.
-   Handles website pop-ups and waits for dynamic content to load.
-   Pauses for manual CAPTCHA entry.
-   Scrapes the resulting cause list table using BeautifulSoup.
-   Generates a well-formatted PDF report with text wrapping and styling using ReportLab.

### Prerequisites

Before you run the script, you need to have Python 3 and the following libraries installed. You will also need Google Chrome and the corresponding ChromeDriver.

1.  **Install Python libraries:**
    ```bash
    pip install selenium beautifulsoup4 reportlab
    ```

2.  **ChromeDriver:**
    -   Make sure you have Google Chrome installed.
    -   Download the ChromeDriver that matches your Chrome version from the [official site](https://googlechromelabs.github.io/chrome-for-testing/).
    -   Ensure `chromedriver.exe` is in your system's PATH or in the same directory as the script. Selenium 4's `WebDriverManager` should handle this automatically in most cases, but manual setup is a reliable fallback.

### How to Run the Script

1.  Open a terminal or command prompt.
2.  Navigate to the directory where `scraper.py` is located.
3.  Run the script:
    ```bash
    python scraper.py
    ```
4.  A Chrome browser window will open and navigate the site.
5.  The script will pause and prompt you in the terminal:
    `⚠️ Please solve the CAPTCHA in browser, then press Enter here to continue...`
6.  Switch to the Chrome window, solve the CAPTCHA, and then press `Enter` in your terminal.
7.  The script will proceed to scrape the data and generate a file named `cause_list_output.pdf` in the same directory.

### Customizing the Scraper for Your Needs

To get the cause list for a different court or date, you will need to modify some hardcoded values in the `scraper.py` file. Here are the key sections to change:

#### 1. State Selection (Line 92)

Change `"Telangana"` to your desired state.

```python
# --- a/c:\Users\yemul\Desktop\scraper.py
# +++ b/c:\Users\yemul\Desktop\scraper.py
# @@ -89,7 +89,7 @@
 # State
 state_dropdown = wait.until(
     EC.presence_of_element_located((By.ID, "sess_state_code")))
-Select(state_dropdown).select_by_visible_text("Telangana")
+Select(state_dropdown).select_by_visible_text("Your State Name") # e.g., "Maharashtra"
 print("✅ Selected state: Telangana")
 time.sleep(2)
```

#### 2. District Selection (Line 102)

After setting the state, change `"Hyderabad"` to the district you are interested in.

```python
# --- a/c:\Users\yemul\Desktop\scraper.py
# +++ b/c:\Users\yemul\Desktop\scraper.py
# @@ -99,7 +99,7 @@
     if len(options) > 1:
         break
     time.sleep(2)
-Select(district_dropdown).select_by_visible_text("Hyderabad")
+Select(district_dropdown).select_by_visible_text("Your District Name") # e.g., "Pune"
 print("✅ Selected district: Hyderabad")
 time.sleep(2)
```

#### 3. Court Complex Selection (Line 108)

The script currently selects the first court complex from the list (`select_by_index(1)`). You may need to change this index or select by name if you know it.

```python
# --- a/c:\Users\yemul\Desktop\scraper.py
# +++ b/c:\Users\yemul\Desktop\scraper.py
# @@ -105,7 +105,8 @@
 print("Waiting for court complexes to load...")
 court_complex_dropdown = wait.until(
     EC.presence_of_element_located((By.ID, "court_complex_code")))
-Select(court_complex_dropdown).select_by_index(1)
+# To select by name:
+# Select(court_complex_dropdown).select_by_visible_text("Name of Court Complex")
+Select(court_complex_dropdown).select_by_index(1) # Change index if needed
 print("✅ Selected court complex by index 1.")
 time.sleep(2)
```

#### 4. Court Name Selection (Line 118)

The script automatically selects the first *enabled* court name. If you want a specific court, you should modify this logic to select by its visible text.

```python
# --- a/c:\Users\yemul\Desktop\scraper.py
# +++ b/c:\Users\yemul\Desktop\scraper.py
# @@ -115,14 +115,9 @@
 for idx, opt in enumerate(options):
     print(f"Option {idx}: '{opt.text}', value={opt.get_attribute('value')}")
 
-selected = False
-for idx, opt in enumerate(options[1:], 1):
-    if not opt.get_attribute("disabled") and opt.get_attribute("value").strip():
-        Select(court_name_dropdown).select_by_index(idx)
-        print(f"✅ Selected Court Option {idx}: '{opt.text}'")
-        selected = True
-        break
-if not selected:
-    raise Exception("❌ No enabled, real court name found.")
+# To select a specific court by its name, replace the loop with this:
+try:
+    Select(court_name_dropdown).select_by_visible_text("I ADDL. SPL. COURT FOR CBI CASES")
+    print("✅ Selected a specific court.")
+except Exception as e:
+    raise Exception(f"❌ Could not select the specified court name: {e}")
```

#### 5. Date Selection (Line 134)

Change the date string `"14-10-2025"` to your desired date in `DD-MM-YYYY` format.

```python
# --- a/c:\Users\yemul\Desktop\scraper.py
# +++ b/c:\Users\yemul\Desktop\scraper.py
# @@ -131,7 +131,7 @@
 date_input = wait.until(
     EC.presence_of_element_located((By.ID, "causelist_date")))
 date_input.clear()
-date_input.send_keys("14-10-2025")
+date_input.send_keys("DD-MM-YYYY") # e.g., "25-12-2024"
 print("✅ Entered cause list date: 14-10-2025")
```

#### 6. PDF Output Filename (Line 169)

You can change the name of the output PDF file.

```python
# --- a/c:\Users\yemul\Desktop\scraper.py
# +++ b/c:\Users\yemul\Desktop\scraper.py
# @@ -166,7 +166,7 @@
     rows = [["No Data Found"]]
 
 # Save as PDF
-save_pdf_table(rows, "cause_list_output.pdf")
+save_pdf_table(rows, "my_custom_cause_list.pdf")
 
 driver.quit()
```


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import time
import os
from reportlab.lib.units import inch


def save_pdf_table(rows, filename="cause_list_output.pdf"):
    """Save cause list data as a properly formatted table with text wrapping."""
    if not rows:
        print("⚠️ No rows to save.")
        return

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []

    # Title
    title = Paragraph(
        "<b>Spl. Court for CBI Cases, Hyderabad - Cause List</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Wrap long cell text in Paragraph for proper wrapping
    wrapped_rows = []
    for r in rows:
        wrapped_rows.append([Paragraph(str(cell).replace(
            "View", "").strip(), styles["Normal"]) for cell in r])

    # Table with proper column widths
    col_widths = [0.6 * inch, 1.3 * inch, 3.5 * inch, 1.5 * inch]
    table = Table(wrapped_rows, repeatRows=1, colWidths=col_widths)

    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E88E5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ])
    table.setStyle(table_style)
    elements.append(table)

    doc.build(elements)
    print(f"✅ Cause list PDF saved correctly as '{filename}'")


# ---------- Selenium Automation Starts ----------
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 25)
driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index")

# Close popup if present
try:
    close_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'close') or @aria-label='Close' or text()='×']")))
    close_btn.click()
    print("Popup closed.")
except Exception:
    print("Popup not found, continuing...")

# State
state_dropdown = wait.until(
    EC.presence_of_element_located((By.ID, "sess_state_code")))
Select(state_dropdown).select_by_visible_text("Telangana")
print("✅ Selected state: Telangana")
time.sleep(2)

# District
print("Waiting for districts to load...")
district_dropdown = wait.until(
    EC.presence_of_element_located((By.ID, "sess_dist_code")))
for _ in range(3):
    options = [o.text.strip()
               for o in district_dropdown.find_elements(By.TAG_NAME, "option")]
    if len(options) > 1:
        break
    time.sleep(2)
Select(district_dropdown).select_by_visible_text("Hyderabad")
print("✅ Selected district: Hyderabad")
time.sleep(2)

# Court Complex
print("Waiting for court complexes to load...")
court_complex_dropdown = wait.until(
    EC.presence_of_element_located((By.ID, "court_complex_code")))
Select(court_complex_dropdown).select_by_index(1)
print("✅ Selected court complex by index 1.")
time.sleep(2)

# Court Name
court_name_dropdown = wait.until(
    EC.presence_of_element_located((By.ID, "CL_court_no")))
options = court_name_dropdown.find_elements(By.TAG_NAME, "option")
for idx, opt in enumerate(options):
    print(f"Option {idx}: '{opt.text}', value={opt.get_attribute('value')}")

selected = False
for idx, opt in enumerate(options[1:], 1):
    if not opt.get_attribute("disabled") and opt.get_attribute("value").strip():
        Select(court_name_dropdown).select_by_index(idx)
        print(f"✅ Selected Court Option {idx}: '{opt.text}'")
        selected = True
        break
if not selected:
    raise Exception("❌ No enabled, real court name found.")

# Date input
date_input = wait.until(
    EC.presence_of_element_located((By.ID, "causelist_date")))
date_input.clear()
date_input.send_keys("14-10-2025")
print("✅ Entered cause list date: 14-10-2025")

# CAPTCHA manual step
input("⚠️ Please solve the CAPTCHA in browser, then press Enter here to continue...")

# Submit button
try:
    submit_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@onclick, \"submit_causelist('cri')\")]")))
    submit_button.click()
    print("✅ Clicked on 'Criminal' submit button successfully.")
except TimeoutException:
    raise Exception("❌ Criminal button not found!")

# Wait for result
print("⏳ Waiting for cause list table to load...")
try:
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[@id='CL_result_div']//table")))
    print("✅ Cause list table loaded successfully.")
except TimeoutException:
    print("⚠️ Table not found within time, waiting 10s more...")
    time.sleep(10)

time.sleep(3)

# ---------- Scraping Table ----------
html_content = driver.page_source
soup = BeautifulSoup(html_content, "html.parser")
table = soup.find("table", {"id": "dispTable"})

rows = []
if table:
    for tr in table.find_all("tr"):
        tds = [td.get_text(strip=True, separator=" ")
               for td in tr.find_all(["td", "th"])]
        if tds:
            rows.append(tds)
else:
    print("❌ No cause list table found. Possibly due to invalid captcha or empty data.")
    rows = [["No Data Found"]]

# Save as PDF
save_pdf_table(rows, "cause_list_output.pdf")

driver.quit()

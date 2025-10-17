import streamlit as st
import os

def run_selenium_until_captcha(state, district, court_complex_index, court_name_index, date_str):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select, WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 25)
    driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index")

    try:
        close_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class, 'close') or @aria-label='Close' or text()='×']")))
        close_btn.click()
    except Exception:
        pass

    state_dropdown = wait.until(EC.presence_of_element_located((By.ID, "sess_state_code")))
    Select(state_dropdown).select_by_visible_text(state)
    time.sleep(2)

    district_dropdown = wait.until(EC.presence_of_element_located((By.ID, "sess_dist_code")))
    for _ in range(3):
        options = [o.text.strip() for o in district_dropdown.find_elements(By.TAG_NAME, "option")]
        if len(options) > 1:
            break
        time.sleep(2)
    Select(district_dropdown).select_by_visible_text(district)
    time.sleep(2)

    court_complex_dropdown = wait.until(EC.presence_of_element_located((By.ID, "court_complex_code")))
    Select(court_complex_dropdown).select_by_index(court_complex_index)
    time.sleep(2)

    court_name_dropdown = wait.until(EC.presence_of_element_located((By.ID, "CL_court_no")))
    Select(court_name_dropdown).select_by_index(court_name_index)
    time.sleep(2)

    date_input = wait.until(EC.presence_of_element_located((By.ID, "causelist_date")))
    date_input.clear()
    date_input.send_keys(date_str)
    time.sleep(1)

    # Store driver in session_state to continue later
    st.session_state['selenium_driver'] = driver

def continue_and_generate_pdf(case_type):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    from bs4 import BeautifulSoup
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    import time

    driver = st.session_state.get('selenium_driver', None)
    if driver is None:
        st.error("Selenium driver instance not found. Please restart the process.")
        return

    wait = WebDriverWait(driver, 25)

    btn_xpath = "//button[contains(@onclick, \"submit_causelist('cri')\")]" if case_type == "Criminal" else "//button[contains(@onclick, \"submit_causelist('civil')\")]"
    try:
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
        submit_button.click()
    except TimeoutException:
        st.error(f"Could not find {case_type} submit button.")
        driver.quit()
        return

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='CL_result_div']//table")))
    except TimeoutException:
        time.sleep(10)

    time.sleep(3)
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
        rows = [["No Data Found"]]

    def save_pdf_table(rows, filename="cause_list_output.pdf"):
        if not rows:
            return
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(filename, pagesize=A4,
                                rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements = []
        title = Paragraph(
            "<b>Spl. Court for CBI Cases, Hyderabad - Cause List</b>", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 12))
        wrapped_rows = []
        for r in rows:
            wrapped_rows.append([Paragraph(str(cell).replace(
                "View", "").strip(), styles["Normal"]) for cell in r])
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

    save_pdf_table(rows, "cause_list_output.pdf")
    driver.quit()
    st.success("PDF generated successfully!")

# ---
# Streamlit UI Flow

st.title("Cause List PDF Downloader")

if "step" not in st.session_state:
    st.session_state.step = "input"

if st.session_state.step == "input":
    with st.form("input_form"):
        state = st.text_input("State", "Telangana")
        district = st.text_input("District", "Hyderabad")
        court_complex_index = st.number_input("Court Complex Index (0-based)", min_value=0, value=1)
        court_name_index = st.number_input("Court Name Index (0-based)", min_value=0, value=1)
        date_str = st.text_input("Cause List Date (dd-mm-yyyy)", "14-10-2025")
        submitted = st.form_submit_button("Start Process")

    if submitted:
        st.session_state.user_inputs = {
            "state": state,
            "district": district,
            "court_complex_index": court_complex_index,
            "court_name_index": court_name_index,
            "date_str": date_str
        }
        run_selenium_until_captcha(
            state,
            district,
            court_complex_index,
            court_name_index,
            date_str
        )
        st.session_state.step = "captcha"
        

elif st.session_state.step == "captcha":
    st.info("Browser opened — please solve CAPTCHA there. Then click below.")
    if st.button("Continue after CAPTCHA"):
        st.session_state.step = "casetype"
        

elif st.session_state.step == "casetype":
    case_type = st.radio("Select Civil or Criminal:", options=["Criminal", "Civil"])
    if st.button("Generate PDF"):
        inputs = st.session_state.user_inputs
        continue_and_generate_pdf(case_type)
        st.session_state.step = "done"
        

elif st.session_state.step == "done":
    if os.path.exists("cause_list_output.pdf"):
        with open("cause_list_output.pdf", "rb") as f:
            st.download_button(
                label="Download Cause List PDF",
                data=f,
                file_name="cause_list_output.pdf",
                mime="application/pdf"
            )
    if st.button("Start Over"):
        st.session_state.step = "input"
        # cleanup session keys
        for key in ["selenium_driver", "user_inputs"]:
            if key in st.session_state:
                del st.session_state[key]
        

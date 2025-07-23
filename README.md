# QA Automation – Parking Lot System

## Project Structure

- **parking_app.py** – Page Object with all API/UI actions.
- **test_parking_app.py** – Main Pytest script with all test cases.
- **requirements.txt** – Python dependencies.
- **report.html** – Test report (auto-generated after running tests).

---

## How to Run the Tests

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run the tests and generate the HTML report:
    ```bash
    pytest --html=report.html --self-contained-html
    ```
   The **report.html** file will be created in the project root directory.

---


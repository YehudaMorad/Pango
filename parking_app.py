# parking_app.py

import requests
from bs4 import BeautifulSoup

class ParkingApp:
    """
    Page Object encapsulating all main flows for the Parking system.
    """
    def __init__(self, base_url):
        self.base_url = base_url
    
    def extract_flash_message(self, html):
        soup = BeautifulSoup(html, "html.parser")
        alert = soup.find(class_=["alert", "alert-danger", "alert-warning", "alert-info"])
        return alert.get_text(strip=True) if alert else ""

    def get_csrf_token(self, session, url):
        resp = session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        token_input = soup.find('input', {'name': 'csrf_token'})
        token = token_input['value'] if token_input else None
        assert token, f"CSRF token not found at {url}!"
        return token

    def login(self, session, username, password):
        login_url = f"{self.base_url}/login"
        csrf_token = self.get_csrf_token(session, login_url)
        login_data = {
            'csrf_token': csrf_token,
            'username': username,
            'password': password,
            'submit': 'Login'
        }
        resp = session.post(login_url, data=login_data, allow_redirects=True)
        assert resp.status_code == 200
        assert "Invalid credentials" not in resp.text
        return resp

    def add_user(self, admin_session, username, password):
        url = f"{self.base_url}/users/add"
        csrf_token = self.get_csrf_token(admin_session, url)
        data = {
            'csrf_token': csrf_token,
            'username': username,
            'password': password,
            'submit': 'Create'
        }
        resp = admin_session.post(url, data=data, allow_redirects=True)
        return resp

    def start_parking(self, session, car_plate, slot, vehicle_type_id='1'):
        dashboard_url = f"{self.base_url}/"
        csrf_token = self.get_csrf_token(session, dashboard_url)
        start_url = f"{self.base_url}/start"
        parking_data = {
            'csrf_token': csrf_token,
            'car_plate': car_plate,
            'vehicle_type_id': vehicle_type_id,
            'slot': slot,
            'submit': 'Start Parking'
        }
        resp = session.post(start_url, data=parking_data, allow_redirects=True)
        return resp

    def get_active_sessions(self, session):
        url = f"{self.base_url}/"
        resp = session.get(url)
        return resp

    def user_exists(self, admin_session, username):
        url = f"{self.base_url}/users"
        resp = admin_session.get(url)
        return username in resp.text


    def close_session_by_plate_and_slot(self, admin_session, car_plate, slot):
        """Find session by car_plate and slot and close it. Returns (session_id, response, message)"""
        from bs4 import BeautifulSoup
        dash = admin_session.get(f"{self.base_url}/").text
        soup = BeautifulSoup(dash, "html.parser")
        session_id = None
        for tr in soup.find_all("tr"):
            if car_plate in tr.text and slot in tr.text:
                form = tr.find("form", {"action": True})
                if form and "/end/" in form['action']:
                    session_id = form['action'].split("/end/")[1]
                    break
        if not session_id:
            return None, None, "Session ID not found"
        csrf_token = self.get_csrf_token(admin_session, self.base_url)
        resp = admin_session.post(f"{self.base_url}/end/{session_id}", data={'csrf_token': csrf_token}, allow_redirects=True)
        msg = self.extract_flash_message(resp.text)
        return session_id, resp, msg
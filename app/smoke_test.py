import requests

BASE = "http://127.0.0.1:8000"

def main():
    s = requests.Session()
    r = s.post(f"{BASE}/auth/register", json={"login": "testuser", "password": "testpassword"})
    if r.status_code not in (200, 201, 409):
        print("register failed", r.status_code, r.text)
        return
    r = s.post(f"{BASE}/auth/login", json={"login": "testuser", "password": "testpassword", "remember": False})
    print("login", r.status_code, r.text)
    r = s.get(f"{BASE}/auth/me")
    print("me", r.status_code, r.text)
    r = s.post(f"{BASE}/auth/logout")
    print("logout", r.status_code, r.text)

if __name__ == "__main__":
    main()

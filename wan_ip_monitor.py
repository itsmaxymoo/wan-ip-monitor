import os
import time
import smtplib
import requests

IP_FILE = './ip.txt'


def get_env_int(var_name, default=5):
    value = os.getenv(var_name, str(default))
    try:
        value = int(value)
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        raise ValueError(f"{var_name} must be a positive integer")


def get_public_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=10).text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to fetch public IP: {e}")
        return None


def read_last_ip():
    try:
        if not os.path.exists(IP_FILE):
            return None
        with open(IP_FILE, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"[ERROR] Failed to read last IP: {e}")
        return None


def write_ip(ip):
    try:
        with open(IP_FILE, 'w') as file:
            file.write(ip)
    except Exception as e:
        print(f"[ERROR] Failed to write IP to file: {e}")


def send_email_notification(new_ip):
    try:
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USERNAME')
        smtp_pass = os.getenv('SMTP_PASSWORD')
        recipient = os.getenv('EMAIL_TO')
        sender = os.getenv('EMAIL_FROM', smtp_user)
        network_name = os.getenv('NETWORK_NAME', 'your network')

        if not all([smtp_host, smtp_port, recipient]):
            print("[ERROR] Missing SMTP configuration.")
            return

        subject = f"WAN IP Change Notification for {network_name}"
        body = f"New public IP address detected for {network_name}:\n\n{new_ip}"
        message = f"Subject: {subject}\nFrom: WAN IP Monitor <{sender}>\nTo: {recipient}\n\n{body}"

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, [recipient], message)
            print(f"[INFO] Email notification sent to {recipient}.")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")


def main():
    try:
        delay_minutes = get_env_int('CHECK_DELAY')
        delay_seconds = delay_minutes * 60
    except ValueError as e:
        print(f"[ERROR] CHECK_DELAY must be a positive integer")
        return

    last_ip = read_last_ip()

    while True:
        try:
            current_ip = get_public_ip()
            
            if current_ip:
                if current_ip != last_ip:
                    print(f"[INFO] New IP detected: {current_ip}")
                    write_ip(current_ip)
                    send_email_notification(current_ip)
                    last_ip = current_ip
                else:
                    print(f"[INFO] Current IP: {current_ip}")
        except Exception as e:
            print(f"[ERROR] {e}")
            
        time.sleep(delay_seconds)


if __name__ == '__main__':
    main()

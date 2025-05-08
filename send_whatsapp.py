from twilio.rest import Client

def send_whatsapp(pdf_path, user_mobile):
    # Twilio credentials
    account_sid = "your_account_sid"
    auth_token = "your_auth_token"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio sandbox number
        to=f'whatsapp:+91{user_mobile}',
        body="Here is your college prediction report.",
        media_url=f"https://your_domain.com/{pdf_path}"
    )
    return message.sid

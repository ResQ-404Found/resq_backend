import firebase_admin
from firebase_admin import messaging, credentials

cred = credentials.Certificate("secrets/firebase_service_account.json")
firebase_admin.initialize_app(cred)

def send_fcm(token, title, body):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )
        messaging.send(message)
        return True
    except Exception as e:
        print(f"[ERROR] FCM 발송 실패: {e}")
        return False
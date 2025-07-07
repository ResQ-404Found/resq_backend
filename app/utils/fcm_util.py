from firebase_admin import messaging

def send_fcm_notification(token: str, title: str, body: str) -> bool:
    print(f"[FCM] token={token} | title={title} | body={body}")
    try:
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(
                title=title,
                body=body
            )
        )
        response = messaging.send(message)
        print(f"[FCM] 성공적으로 전송됨: {response}")
        return True
    except Exception as e:
        print(f"[FCM] 전송 실패: {e}")
        return False
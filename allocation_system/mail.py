import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from allocation_system.config_ini import IniConfig

def send_html_completion_email():
    ini_config = IniConfig()
    
    to_email = ini_config.get("Mail" ,"SENDADDRESS")  # 宛先を入力
    subject = "テストメール"
    html_body = "<html><body><h1>これはテストメールです。</h1></body></html>"

    from_email = "ryosuke_takiguchi@impcode.net"
    from_password = "impcode-admin"  # 実際の環境では環境変数などで管理推奨

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((str(Header("ryosuke_takiguchi", "utf-8")), "ryosuke_takiguchi@impcode.net"))
    msg["To"] = to_email
    msg["Subject"] = Header(subject, "utf-8")

    mime_html = MIMEText(html_body, "html", "utf-8")
    msg.attach(mime_html)

    try:
        with smtplib.SMTP_SSL("impcode.sakura.ne.jp", 465) as server:
            server.ehlo("localhost")
            server.login(from_email, from_password)
            server.send_message(msg)
            print("メール送信に成功しました")
    except Exception as e:
        print(f"メール送信に失敗しました: {e}")



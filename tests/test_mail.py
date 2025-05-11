import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from allocation_system.mail import send_html_completion_email

send_html_completion_email()
input("エンターで終了します")
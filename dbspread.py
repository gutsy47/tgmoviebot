import os
import gspread


class Service:
    def __init__(self):
        credentials = {
            "type": "service_account",
            "project_id": os.environ['GOOGLE_PROJECT_ID'],
            "private_key_id": os.environ["GOOGLE_PRIVATE_KEY_ID"],
            "private_key": os.environ["GOOGLE_PRIVATE_KEY"].replace('\\n', '\n'),
            "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ['GOOGLE_CLIENT_X509_CERT_URL']
        }
        account = gspread.service_account_from_dict(credentials)
        self.spreadsheet = account.open("Bot data")

    def get_post_template(self):
        worksheet = self.spreadsheet.worksheet(title="Шаблон поста")
        return worksheet.cell(1, 1).value.replace('\\n', '\n')

    def update_post_template(self, template: str):
        worksheet = self.spreadsheet.worksheet(title="Шаблон поста")
        worksheet.update_cell(1, 1, template)

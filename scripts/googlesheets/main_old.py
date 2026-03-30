import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret_452250864144-9ou19c040pi9d74nf7jaflnll60gekkg.apps.googleusercontent.com.json",  # ваш файл из Cloud Console
        SCOPES,
    )
    creds = flow.run_local_server(port=0)
    Path("token.json").write_text(creds.to_json(), encoding="utf-8")
    print("Сохранено token.json — храните в секрете, не коммитьте в git")


if __name__ == "__main__":
    main()

# from google.oauth2 import service_account
# from googleapiclient.discovery import build

# SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
# creds = service_account.Credentials.from_service_account_file(
#     "report-project-470505-3e2a3ddfec59.json", scopes=SCOPES
# )
# service = build("drive", "v3", credentials=creds)
# about = service.about().get(fields="storageQuota").execute()
# q = about.get("storageQuota", {})
# # лимит и использование в байтах (часто limit=0 или очень мало)
# for k in ("limit", "usage", "usageInDrive", "usageInDriveTrash"):
#     print(k, q.get(k))

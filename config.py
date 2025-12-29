import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "@digebdjdbdd")

DB_PATH = "data/database.db"
FILES_DIR = "files/pdfs"

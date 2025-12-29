from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_subscription_keyboard(channel_url):
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{channel_url.replace('@', '')}")],
        [InlineKeyboardButton("✅ تم الاشتراك، تحقق الآن", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard(is_admin=False):
    keyboard = [
        [InlineKeyboardButton("🎓 اختر مستواك الدراسي", callback_data="levels")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("🔐 لوحة تحكم الأدمن", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

def get_levels_keyboard(levels):
    keyboard = []
    for level_id, name in levels:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"level_{level_id}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_semesters_keyboard(semesters, level_id):
    keyboard = []
    for sem_id, name in semesters:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"sem_{sem_id}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع للمستويات", callback_data="levels")])
    return InlineKeyboardMarkup(keyboard)

def get_subjects_keyboard(subjects, level_id):
    keyboard = []
    for sub_id, name in subjects:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"sub_{sub_id}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="levels")])
    return InlineKeyboardMarkup(keyboard)

def get_subject_options_keyboard(subject_id):
    keyboard = [
        [InlineKeyboardButton("📘 ملخصات", callback_data=f"content_summary_{subject_id}")],
        [InlineKeyboardButton("📂 ملازم", callback_data=f"content_handout_{subject_id}")],
        [InlineKeyboardButton("🔗 روابط شروحات مفيدة", callback_data=f"content_link_{subject_id}")],
        [InlineKeyboardButton("🔙 رجوع للمواد", callback_data="levels")] # Simplified back
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ إضافة مادة", callback_data="admin_add_subject")],
        [InlineKeyboardButton("➕ إضافة محتوى", callback_data="admin_add_content")],
        [InlineKeyboardButton("📢 إرسال رسالة جماعية", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 خروج من لوحة التحكم", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

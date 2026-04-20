from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_subscription_keyboard(channel_url):
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{channel_url.replace('@', '')}")],
        [InlineKeyboardButton("✅ تم الاشتراك، تحقق الآن", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard(role='user'):
    keyboard = [
        [InlineKeyboardButton("🎓 اختر مستواك الدراسي", callback_data="levels")]
    ]
    if role == 'admin':
        keyboard.append([InlineKeyboardButton("🔐 لوحة تحكم السوبر أدمن", callback_data="admin_panel")])
    elif role == 'delegate':
        keyboard.append([InlineKeyboardButton("🛠️ لوحة تحكم المندوب", callback_data="delegate_panel")])
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
        [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ إضافة مادة", callback_data="admin_add_subject")],
        [InlineKeyboardButton("➕ إضافة محتوى", callback_data="admin_add_content")],
        [InlineKeyboardButton("🗑️ حذف محتوى/مادة", callback_data="admin_delete_start")],
        [InlineKeyboardButton("👤 إدارة المندوبين", callback_data="admin_manage_delegates")],
        [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban_user")],
        [InlineKeyboardButton("📢 إرسال رسالة جماعية", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 خروج", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_delegate_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ إضافة مادة (لمستواي)", callback_data="admin_add_subject")],
        [InlineKeyboardButton("➕ إضافة محتوى (لمستواي)", callback_data="admin_add_content")],
        [InlineKeyboardButton("🗑️ حذف محتوى (لمستواي)", callback_data="admin_delete_start")],
        [InlineKeyboardButton("🔙 خروج", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import config
from keyboards.keyboards import get_admin_keyboard, get_levels_keyboard, get_semesters_keyboard, get_subjects_keyboard

# Conversation states
ADD_SUB_LEVEL = 1
ADD_SUB_SEM = 2
ADD_SUB_NAME = 3

ADD_CONTENT_SUB = 4
ADD_CONTENT_TYPE = 5
ADD_CONTENT_TITLE = 6
ADD_CONTENT_DATA = 7

DELETE_SUB_SELECT = 8
BROADCAST_MSG = 9

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != config.ADMIN_ID:
        if update.callback_query:
            await update.callback_query.answer("🚫 غير مصرح لك.", show_alert=True)
        return ConversationHandler.END
    
    text = "🛠️ لوحة تحكم الأدمن:\nيمكنك إدارة المواد والمحتوى من هنا."
    reply_markup = get_admin_keyboard()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
    return ConversationHandler.END

# --- Add Subject ---
async def start_add_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    levels = context.bot_data['db'].get_levels()
    await update.callback_query.edit_message_text("اختر المستوى لإضافة مادة فيه:", reply_markup=get_levels_keyboard(levels))
    return ADD_SUB_LEVEL

async def add_sub_level_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    level_id = int(query.data.split('_')[1])
    context.user_data['admin_level'] = level_id
    semesters = context.bot_data['db'].get_semesters(level_id)
    await query.edit_message_text("حدد الترم الدراسي:", reply_markup=get_semesters_keyboard(semesters, level_id))
    return ADD_SUB_SEM

async def add_sub_sem_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    sem_id = int(query.data.split('_')[1])
    context.user_data['admin_sem'] = sem_id
    await query.edit_message_text("📝 أرسل اسم المادة الجديدة الآن:")
    return ADD_SUB_NAME

async def save_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sub_name = update.message.text
    sem_id = context.user_data['admin_sem']
    context.bot_data['db'].add_subject(sem_id, sub_name)
    await update.message.reply_text(f"✅ تم إضافة مادة '{sub_name}' بنجاح!", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

# --- Add Content ---
async def start_add_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    levels = context.bot_data['db'].get_levels()
    await update.callback_query.edit_message_text("اختر المستوى الدراسي للمادة:", reply_markup=get_levels_keyboard(levels))
    return ADD_CONTENT_SUB

async def add_content_level_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    level_id = int(query.data.split('_')[1])
    semesters = context.bot_data['db'].get_semesters(level_id)
    await query.edit_message_text("حدد الترم الدراسي:", reply_markup=get_semesters_keyboard(semesters, level_id))
    return ADD_CONTENT_SUB # Reuse state for simplicity

async def add_content_sem_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    sem_id = int(query.data.split('_')[1])
    subjects = context.bot_data['db'].get_subjects(sem_id)
    if not subjects:
        await query.answer("⚠️ لا توجد مواد في هذا الترم.", show_alert=True)
        return ADD_CONTENT_SUB
    await query.edit_message_text("اختر المادة لإضافة محتوى لها:", reply_markup=get_subjects_keyboard(subjects, 0))
    return ADD_CONTENT_TYPE

async def add_content_sub_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    sub_id = int(query.data.split('_')[1])
    context.user_data['admin_sub'] = sub_id
    keyboard = [
        [InlineKeyboardButton("📘 ملخص", callback_data="type_summary")],
        [InlineKeyboardButton("📂 ملزمة", callback_data="type_handout")],
        [InlineKeyboardButton("🔗 رابط", callback_data="type_link")]
    ]
    await query.edit_message_text("اختر نوع المحتوى:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ADD_CONTENT_TITLE

async def add_content_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    c_type = query.data.split('_')[1]
    context.user_data['admin_content_type'] = c_type
    await query.edit_message_text("📝 أرسل عنواناً لهذا المحتوى (مثلاً: ملخص الفصل الأول):")
    return ADD_CONTENT_DATA

async def add_content_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['admin_content_title'] = update.message.text
    c_type = context.user_data['admin_content_type']
    if c_type == 'link':
        await update.message.reply_text("🔗 أرسل الرابط الآن:")
    else:
        await update.message.reply_text("📄 أرسل ملف الـ PDF الآن:")
    return ADD_CONTENT_DATA

async def save_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sub_id = context.user_data['admin_sub']
    c_type = context.user_data['admin_content_type']
    title = context.user_data['admin_content_title']
    
    if c_type == 'link':
        url = update.message.text
        context.bot_data['db'].add_content(sub_id, c_type, title, url=url)
    else:
        if not update.message.document:
            await update.message.reply_text("❌ يرجى إرسال ملف PDF.")
            return ADD_CONTENT_DATA
        file_id = update.message.document.file_id
        context.bot_data['db'].add_content(sub_id, c_type, title, file_id=file_id)
    
    await update.message.reply_text("✅ تم إضافة المحتوى بنجاح!", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

# --- Broadcast ---
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("📝 أرسل الرسالة التي تريد تعميمها:")
    return BROADCAST_MSG

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    users = context.bot_data['db'].get_all_users()
    count = 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 رسالة من الإدارة:\n\n{msg}")
            count += 1
        except: continue
    await update.message.reply_text(f"✅ تم الإرسال إلى {count} مستخدم.", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الإلغاء.", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

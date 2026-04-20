from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import config
from keyboards.keyboards import get_admin_keyboard, get_delegate_keyboard, get_levels_keyboard, get_semesters_keyboard, get_subjects_keyboard

# Conversation states
ADD_SUB_LEVEL, ADD_SUB_SEM, ADD_SUB_NAME = range(1, 4)
ADD_CONTENT_SUB, ADD_CONTENT_TYPE, ADD_CONTENT_TITLE, ADD_CONTENT_DATA = range(4, 8)
MANAGE_DELEGATES, BAN_USER, BROADCAST_MSG, DELETE_CONTENT = range(8, 12)

async def check_admin_privileges(update: Update, context: ContextTypes.DEFAULT_TYPE, required_role='delegate'):
    user_id = update.effective_user.id
    user_data = context.bot_data['db'].get_user(user_id)
    if not user_data: return False
    
    role = user_data[2]
    if role == 'admin': return True
    if required_role == 'delegate' and role == 'delegate': return True
    return False

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = context.bot_data['db'].get_user(user_id)
    role = user_data[2] if user_data else 'user'
    
    if role == 'admin':
        text = "🛠️ لوحة تحكم السوبر أدمن:"
        reply_markup = get_admin_keyboard()
    elif role == 'delegate':
        text = f"🛠️ لوحة تحكم المندوب (المستوى: {user_data[3]}):"
        reply_markup = get_delegate_keyboard()
    else:
        if update.callback_query: await update.callback_query.answer("🚫 غير مصرح لك.", show_alert=True)
        return ConversationHandler.END
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
    return ConversationHandler.END

# --- Add Subject ---
async def start_add_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_privileges(update, context): return ConversationHandler.END
    
    user_id = update.effective_user.id
    user_data = context.bot_data['db'].get_user(user_id)
    
    if user_data[2] == 'delegate':
        level_id = user_data[3]
        context.user_data['admin_level'] = level_id
        semesters = context.bot_data['db'].get_semesters(level_id)
        await update.callback_query.edit_message_text("حدد الترم الدراسي:", reply_markup=get_semesters_keyboard(semesters, level_id))
        return ADD_SUB_SEM
    
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
    await update.message.reply_text(f"✅ تم إضافة مادة '{sub_name}' بنجاح!")
    return ConversationHandler.END

# --- Add Content ---
async def start_add_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_privileges(update, context): return ConversationHandler.END
    
    user_id = update.effective_user.id
    user_data = context.bot_data['db'].get_user(user_id)
    
    if user_data[2] == 'delegate':
        level_id = user_data[3]
        semesters = context.bot_data['db'].get_semesters(level_id)
        await update.callback_query.edit_message_text("حدد الترم الدراسي:", reply_markup=get_semesters_keyboard(semesters, level_id))
        return ADD_CONTENT_SUB
        
    levels = context.bot_data['db'].get_levels()
    await update.callback_query.edit_message_text("اختر المستوى الدراسي للمادة:", reply_markup=get_levels_keyboard(levels))
    return ADD_CONTENT_SUB

async def add_content_level_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    level_id = int(query.data.split('_')[1])
    semesters = context.bot_data['db'].get_semesters(level_id)
    await query.edit_message_text("حدد الترم الدراسي:", reply_markup=get_semesters_keyboard(semesters, level_id))
    return ADD_CONTENT_SUB

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
    await query.edit_message_text("📝 أرسل عنواناً لهذا المحتوى:")
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
    user_id = update.effective_user.id
    
    if c_type == 'link':
        url = update.message.text
        context.bot_data['db'].add_content(sub_id, c_type, title, user_id, url=url)
    else:
        if not update.message.document:
            await update.message.reply_text("❌ يرجى إرسال ملف PDF.")
            return ADD_CONTENT_DATA
        file_id = update.message.document.file_id
        context.bot_data['db'].add_content(sub_id, c_type, title, user_id, file_id=file_id)
    
    await update.message.reply_text("✅ تم إضافة المحتوى بنجاح!")
    return ConversationHandler.END

# --- Manage Delegates (Super Admin Only) ---
async def start_manage_delegates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_privileges(update, context, 'admin'): return ConversationHandler.END
    await update.callback_query.edit_message_text("👤 أرسل ID المستخدم لتعيينه كمندوب:")
    return MANAGE_DELEGATES

async def save_delegate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_id = int(update.message.text)
        # For simplicity, we'll ask for level after ID
        context.user_data['target_delegate_id'] = target_id
        levels = context.bot_data['db'].get_levels()
        await update.message.reply_text("اختر المستوى لهذا المندوب:", reply_markup=get_levels_keyboard(levels))
        return MANAGE_DELEGATES
    except ValueError:
        await update.message.reply_text("❌ يرجى إرسال ID صحيح (أرقام فقط).")
        return MANAGE_DELEGATES

async def delegate_level_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    level_id = int(query.data.split('_')[1])
    target_id = context.user_data['target_delegate_id']
    context.bot_data['db'].update_user_role(target_id, 'delegate', level_id)
    await query.edit_message_text(f"✅ تم تعيين المستخدم {target_id} كمندوب للمستوى {level_id}.")
    return ConversationHandler.END

# --- Ban User (Super Admin Only) ---
async def start_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_privileges(update, context, 'admin'): return ConversationHandler.END
    await update.callback_query.edit_message_text("🚫 أرسل ID المستخدم لحظره:")
    return BAN_USER

async def save_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_id = int(update.message.text)
        context.bot_data['db'].set_ban_status(target_id, 1)
        await update.message.reply_text(f"✅ تم حظر المستخدم {target_id} بنجاح.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ يرجى إرسال ID صحيح.")
        return BAN_USER

# --- Broadcast ---
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_privileges(update, context, 'admin'): return ConversationHandler.END
    await update.callback_query.edit_message_text("📝 أرسل الرسالة الجماعية:")
    return BROADCAST_MSG

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    users = context.bot_data['db'].get_all_users()
    count = 0
    for u_id, _, _, _ in users:
        try:
            await context.bot.send_message(chat_id=u_id, text=f"📢 رسالة من الإدارة:\n\n{msg}")
            count += 1
        except: continue
    await update.message.reply_text(f"✅ تم الإرسال إلى {count} مستخدم.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الإلغاء.")
    return ConversationHandler.END

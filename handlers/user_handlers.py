from telegram import Update
from telegram.ext import ContextTypes
from keyboards.keyboards import (
    get_subscription_keyboard, get_main_keyboard, get_levels_keyboard,
    get_semesters_keyboard, get_subjects_keyboard, get_subject_options_keyboard
)
import config

async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=config.REQUIRED_CHANNEL, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return True # Safety fallback

async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = context.bot_data['db'].get_user(user_id)
    
    if user_data and user_data[4] == 1: # is_banned
        await update.effective_message.reply_text("🚫 عذراً، لقد تم حظرك من استخدام البوت.")
        return False
    
    if not await is_subscribed(update, context):
        await show_subscription_msg(update, context)
        return False
    
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Initial role setup
    role = 'admin' if user.id == config.ADMIN_ID else 'user'
    context.bot_data['db'].add_user(user.id, user.username, role=role)
    
    if await check_user_status(update, context):
        await show_main_menu(update, context)

async def show_subscription_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "⚠️ عذراً، يجب عليك الاشتراك في قناة البوت أولاً لاستخدام الخدمات."
    reply_markup = get_subscription_keyboard(config.REQUIRED_CHANNEL)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await is_subscribed(update, context):
        await query.answer("✅ تم التحقق بنجاح!")
        await show_main_menu(update, context)
    else:
        await query.answer("❌ لم تشترك في القناة بعد!", show_alert=True)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = context.bot_data['db'].get_user(user_id)
    role = user_data[2] if user_data else 'user'
    
    text = "👋 أهلاً بك في بوت دليل الطالب الجامعي.\n\nيرجى اختيار ما تريد من الأزرار أدناه:"
    reply_markup = get_main_keyboard(role)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_status(update, context): return
    query = update.callback_query
    levels = context.bot_data['db'].get_levels()
    reply_markup = get_levels_keyboard(levels)
    await query.edit_message_text("📚 اختر مستواك الدراسي:", reply_markup=reply_markup)

async def handle_level_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_status(update, context): return
    query = update.callback_query
    level_id = int(query.data.split('_')[1])
    context.user_data['selected_level'] = level_id
    semesters = context.bot_data['db'].get_semesters(level_id)
    reply_markup = get_semesters_keyboard(semesters, level_id)
    await query.edit_message_text("📅 حدد الترم الدراسي:", reply_markup=reply_markup)

async def handle_semester_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_status(update, context): return
    query = update.callback_query
    sem_id = int(query.data.split('_')[1])
    context.user_data['selected_sem'] = sem_id
    subjects = context.bot_data['db'].get_subjects(sem_id)
    if not subjects:
        await query.answer("⚠️ لا توجد مواد مضافة لهذا الترم حالياً.", show_alert=True)
        return
    reply_markup = get_subjects_keyboard(subjects, context.user_data['selected_level'])
    await query.edit_message_text("📖 اختر المادة:", reply_markup=reply_markup)

async def handle_subject_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_status(update, context): return
    query = update.callback_query
    sub_id = int(query.data.split('_')[1])
    context.user_data['selected_sub'] = sub_id
    reply_markup = get_subject_options_keyboard(sub_id)
    await query.edit_message_text("🛠️ اختر نوع المحتوى الذي تبحث عنه:", reply_markup=reply_markup)

async def handle_content_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user_status(update, context): return
    query = update.callback_query
    data = query.data.split('_')
    content_type = data[1]
    sub_id = int(data[2])
    
    contents = context.bot_data['db'].get_content(sub_id, content_type)
    
    if not contents:
        await query.answer("⚠️ لا يوجد محتوى متوفر حالياً.", show_alert=True)
        return

    if content_type == 'link':
        text = "🔗 **روابط الشروحات المفيدة:**\n\n"
        for _, title, _, url in contents:
            text += f"🔹 {title}\n🔗 {url}\n\n"
        await query.message.reply_text(text, parse_mode='Markdown')
    else:
        for _, title, file_id, _ in contents:
            try:
                await query.message.reply_document(document=file_id, caption=f"📄 {title}")
            except Exception:
                await query.message.reply_text(f"❌ خطأ في إرسال الملف: {title}")
    
    await query.answer()

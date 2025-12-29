from telegram import Update
from telegram.ext import ContextTypes
from keyboards.keyboards import (
    get_subscription_keyboard, get_main_keyboard, get_levels_keyboard,
    get_semesters_keyboard, get_subjects_keyboard, get_subject_options_keyboard
)
import config

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.bot_data['db'].add_user(user.id, user.username)
    
    # Check subscription
    try:
        member = await context.bot.get_chat_member(chat_id=config.REQUIRED_CHANNEL, user_id=user.id)
        if member.status in ['member', 'administrator', 'creator']:
            await show_main_menu(update, context)
        else:
            await show_subscription_msg(update, context)
    except Exception:
        # If bot is not admin in channel or channel not found, skip check for safety
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
    user_id = query.from_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=config.REQUIRED_CHANNEL, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await query.answer("✅ تم التحقق بنجاح!")
            await show_main_menu(update, context)
        else:
            await query.answer("❌ لم تشترك في القناة بعد!", show_alert=True)
    except Exception:
        await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = (user_id == config.ADMIN_ID)
    text = "👋 أهلاً بك في بوت دليل الطالب الجامعي.\n\nيرجى اختيار ما تريد من الأزرار أدناه:"
    reply_markup = get_main_keyboard(is_admin)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    levels = context.bot_data['db'].get_levels()
    reply_markup = get_levels_keyboard(levels)
    await query.edit_message_text("📚 اختر مستواك الدراسي:", reply_markup=reply_markup)

async def handle_level_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    level_id = int(query.data.split('_')[1])
    context.user_data['selected_level'] = level_id
    semesters = context.bot_data['db'].get_semesters(level_id)
    reply_markup = get_semesters_keyboard(semesters, level_id)
    await query.edit_message_text("📅 حدد الترم الدراسي:", reply_markup=reply_markup)

async def handle_semester_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    query = update.callback_query
    sub_id = int(query.data.split('_')[1])
    context.user_data['selected_sub'] = sub_id
    reply_markup = get_subject_options_keyboard(sub_id)
    await query.edit_message_text("🛠️ اختر نوع المحتوى الذي تبحث عنه:", reply_markup=reply_markup)

async def handle_content_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split('_')
    content_type = data[1] # summary, handout, link
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
        # For PDF files (summaries and handouts)
        for _, title, file_id, _ in contents:
            try:
                await query.message.reply_document(document=file_id, caption=f"📄 {title}")
            except Exception as e:
                await query.message.reply_text(f"❌ خطأ في إرسال الملف: {title}")
    
    await query.answer()

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, ConversationHandler
)
import config
from data.database import Database
from handlers.user_handlers import (
    start, check_subscription, handle_levels, handle_level_selection,
    handle_semester_selection, handle_subject_selection, handle_content_view,
    show_main_menu
)
from handlers.admin_handlers import (
    admin_panel, start_add_subject, add_sub_level_selected, add_sub_sem_selected, save_subject,
    start_add_content, add_content_level_selected, add_content_sem_selected, add_content_sub_selected,
    add_content_type_selected, add_content_title_received, save_content,
    start_broadcast, send_broadcast, cancel,
    ADD_SUB_LEVEL, ADD_SUB_SEM, ADD_SUB_NAME,
    ADD_CONTENT_SUB, ADD_CONTENT_TYPE, ADD_CONTENT_TITLE, ADD_CONTENT_DATA,
    BROADCAST_MSG
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(f"Exception while handling an update: {context.error}")

def main():
    db = Database(config.DB_PATH)
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    application.bot_data['db'] = db

    # Admin Conversation Handlers
    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_panel, pattern="^admin_panel$"),
            CallbackQueryHandler(start_add_subject, pattern="^admin_add_subject$"),
            CallbackQueryHandler(start_add_content, pattern="^admin_add_content$"),
            CallbackQueryHandler(start_broadcast, pattern="^admin_broadcast$")
        ],
        states={
            ADD_SUB_LEVEL: [CallbackQueryHandler(add_sub_level_selected, pattern="^level_")],
            ADD_SUB_SEM: [CallbackQueryHandler(add_sub_sem_selected, pattern="^sem_")],
            ADD_SUB_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_subject)],
            
            ADD_CONTENT_SUB: [
                CallbackQueryHandler(add_content_level_selected, pattern="^level_"),
                CallbackQueryHandler(add_content_sem_selected, pattern="^sem_")
            ],
            ADD_CONTENT_TYPE: [CallbackQueryHandler(add_content_sub_selected, pattern="^sub_")],
            ADD_CONTENT_TITLE: [CallbackQueryHandler(add_content_type_selected, pattern="^type_")],
            ADD_CONTENT_DATA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_content_title_received),
                MessageHandler(filters.Document.PDF, save_content),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_content) # For links
            ],
            BROADCAST_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast)]
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
        allow_reentry=True
    )

    application.add_handler(admin_conv)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(handle_levels, pattern="^levels$"))
    application.add_handler(CallbackQueryHandler(handle_level_selection, pattern="^level_"))
    application.add_handler(CallbackQueryHandler(handle_semester_selection, pattern="^sem_"))
    application.add_handler(CallbackQueryHandler(handle_subject_selection, pattern="^sub_"))
    application.add_handler(CallbackQueryHandler(handle_content_view, pattern="^content_"))
    
    application.add_error_handler(error_handler)

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()

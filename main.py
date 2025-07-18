# main.py
from batch_renamer.ui.main_window import BatchRename
from batch_renamer.logging_config import setup_logging

def main():
    # Initialize logging
    logger = setup_logging()
    logger.info("Starting BatchRename application")
    
    try:
        app = BatchRename()
        logger.info("GUI initialized successfully")
        app.mainloop()
    except Exception as e:
        logger.exception("Unhandled exception in main loop")
        raise
    finally:
        logger.info("Application shutting down")

if __name__ == "__main__":
    main()

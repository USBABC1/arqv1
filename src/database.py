from flask_sqlalchemy import SQLAlchemy
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_database(app):
    """Initialize database with proper error handling"""
    try:
        db.init_app(app)
        logger.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False

def test_database_connection(app):
    """Test database connection"""
    try:
        with app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1'))
            logger.info("✅ Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False
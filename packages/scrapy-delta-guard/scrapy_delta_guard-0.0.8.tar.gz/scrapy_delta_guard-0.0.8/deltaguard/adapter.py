
import logging

logger = logging.getLogger(__name__)



class DeltaGuardAdapter:
    """
    A simple adapter class to standardize attaching SQLAlchemy database objects
    to Scrapy items for DeltaGuard extension consumption.
    """
    @staticmethod
    def attach(item, db_item):
        """
        Attaches the database object to the item under the key 'db_item'.

        Args:
            item (scrapy.Item or dict): The item being processed.
            db_item (object): The SQLAlchemy object fetched from the database.
        """
        if db_item:
            item['db_item'] = db_item




# ============================================================================
# Utility Function for Safe Database Commits
# ============================================================================

def safe_commit(session, spider, force_commit=False):
    """
    Safely commits a SQLAlchemy session, checking the DeltaGuard high delta flag.
    
    Args:
        session: SQLAlchemy session to commit or rollback
        spider: Scrapy spider instance
        force_commit: If True, commits even if delta flag is set (default: False)
    
    Returns:
        bool: True if committed successfully, False if rolled back
    
    Example:
        from deltaguard.extension import safe_commit
        
        class YourPipeline:
            def close_spider(self, spider):
                safe_commit(self.session, spider)
                self.session.close()
    """
    high_delta_detected = getattr(spider, 'delta_guard_high_delta_detected', False)
    
    if high_delta_detected and not force_commit:
        logger.warning(
            "DeltaGuard: High delta flag detected. Rolling back session to prevent data corruption."
        )
        try:
            session.rollback()
            return False
        except Exception as e:
            logger.error(f"DeltaGuard: Error during rollback: {e}")
            return False
    
    try:
        session.commit()
        logger.debug("DeltaGuard: Session committed successfully.")
        return True
    except Exception as e:
        logger.error(f"DeltaGuard: Error during commit: {e}. Rolling back.")
        try:
            session.rollback()
        except Exception as rollback_error:
            logger.error(f"DeltaGuard: Error during rollback: {rollback_error}")
        return False

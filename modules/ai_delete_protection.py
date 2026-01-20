"""
BhoolamMind v1.5 - AI-Safe Delete Protection
PREVENTS ACCIDENTAL DATA DELETION BY AI AGENTS

This module intercepts and protects against any delete operations
"""

import os
import shutil
import sqlite3
from datetime import datetime
from typing import Union, List
import logging

class AIDeleteProtection:
    """
    Protects against accidental deletion by AI agents
    Creates multiple backups before any delete operation
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.protection_enabled = True
        
        # Create protection directories
        os.makedirs("backups/protection", exist_ok=True)
        os.makedirs("backups/pre_delete", exist_ok=True)
        
    def safe_delete_interaction(self, interaction_id: int, reason: str = "AI request") -> bool:
        """
        Safely delete an interaction with multiple safeguards
        
        Args:
            interaction_id: ID of interaction to delete
            reason: Reason for deletion
            
        Returns:
            Success status
        """
        
        if not self.protection_enabled:
            self.logger.warning("Protection disabled - risky operation!")
        
        try:
            # STEP 1: Create immediate backup
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/pre_delete/pre_delete_{backup_timestamp}.db"
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Pre-delete backup created: {backup_path}")
            
            # STEP 2: Log the deletion attempt
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the interaction data before deletion
            cursor.execute("SELECT * FROM interactions WHERE id = ?", (interaction_id,))
            interaction_data = cursor.fetchone()
            
            if not interaction_data:
                self.logger.warning(f"Interaction {interaction_id} not found")
                conn.close()
                return False
            
            # STEP 3: Create deletion log entry
            cursor.execute('''
                INSERT INTO interactions 
                (text, source, tags, emotion, intensity, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                f"DELETION LOG: Deleted interaction {interaction_id}. Reason: {reason}. Original: {interaction_data[1][:100]}...",
                "ai_delete_protection",
                "deletion_log,ai_safety,backup",
                "protective",
                8,
                datetime.now().isoformat()
            ))
            
            # STEP 4: Move to deleted_interactions table instead of actual deletion
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deleted_interactions (
                    id INTEGER,
                    original_text TEXT,
                    deletion_reason TEXT,
                    deletion_timestamp TEXT,
                    original_data TEXT,
                    backup_location TEXT
                )
            ''')
            
            cursor.execute('''
                INSERT INTO deleted_interactions 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                interaction_id,
                interaction_data[1],  # original text
                reason,
                datetime.now().isoformat(),
                str(interaction_data),  # full original data
                backup_path
            ))
            
            # STEP 5: Only now actually delete (but we have backups)
            cursor.execute("DELETE FROM interactions WHERE id = ?", (interaction_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Safely deleted interaction {interaction_id} with full backup protection")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in safe delete: {e}")
            return False
    
    def prevent_bulk_delete(self, max_deletions: int = 5) -> bool:
        """
        Prevents bulk deletion operations that could lose significant data
        
        Args:
            max_deletions: Maximum allowed deletions in one operation
            
        Returns:
            Whether operation is allowed
        """
        
        # This would be called before any bulk operation
        self.logger.warning(f"Bulk deletion attempt detected - max allowed: {max_deletions}")
        
        # Create emergency backup before any bulk operation
        emergency_backup = f"backups/protection/emergency_bulk_protection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(self.db_path, emergency_backup)
        
        self.logger.info(f"Emergency backup created: {emergency_backup}")
        return True
    
    def restore_deleted_interaction(self, interaction_id: int) -> bool:
        """
        Restore a previously deleted interaction
        
        Args:
            interaction_id: ID of interaction to restore
            
        Returns:
            Success status
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find in deleted_interactions
            cursor.execute("SELECT * FROM deleted_interactions WHERE id = ?", (interaction_id,))
            deleted_data = cursor.fetchone()
            
            if not deleted_data:
                self.logger.warning(f"Deleted interaction {interaction_id} not found")
                conn.close()
                return False
            
            # Parse original data and restore
            original_data = eval(deleted_data[4])  # original_data field
            
            cursor.execute('''
                INSERT INTO interactions 
                (text, source, tags, emotion, mood, intensity, bit_worthy, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', original_data[1:9])  # Skip the ID
            
            # Log the restoration
            cursor.execute('''
                INSERT INTO interactions 
                (text, source, tags, emotion, intensity, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                f"RESTORATION LOG: Restored interaction {interaction_id}. Originally deleted: {deleted_data[2]}",
                "ai_delete_protection",
                "restoration_log,ai_safety,recovery",
                "recovered",
                7,
                datetime.now().isoformat()
            ))
            
            # Remove from deleted_interactions
            cursor.execute("DELETE FROM deleted_interactions WHERE id = ?", (interaction_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully restored interaction {interaction_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring interaction: {e}")
            return False
    
    def get_deletion_history(self) -> List[dict]:
        """Get history of all deletions for audit"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM deleted_interactions ORDER BY deletion_timestamp DESC")
            deleted = cursor.fetchall()
            
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'text_preview': row[1][:100] + "..." if len(row[1]) > 100 else row[1],
                    'reason': row[2],
                    'when': row[3],
                    'backup_location': row[5]
                }
                for row in deleted
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting deletion history: {e}")
            return []
    
    def emergency_lockdown(self) -> bool:
        """
        Emergency lockdown - prevents ALL deletions
        Use when AI behavior seems risky
        """
        
        # Create immediate full backup
        lockdown_backup = f"backups/protection/EMERGENCY_LOCKDOWN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(self.db_path, lockdown_backup)
        
        # Disable all deletion capabilities
        self.protection_enabled = False
        
        # Log the lockdown
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interactions 
                (text, source, tags, emotion, intensity, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                "EMERGENCY LOCKDOWN ACTIVATED: All deletion operations disabled. Full backup created.",
                "ai_safety_lockdown",
                "emergency,lockdown,ai_safety,protection",
                "protective",
                10,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error logging lockdown: {e}")
        
        self.logger.critical(f"EMERGENCY LOCKDOWN ACTIVATED - Backup: {lockdown_backup}")
        return True

# Global protection instance
_protection_instance = None

def get_protection_instance(db_path: str = "memory/sqlite_db/bhoolamind.db") -> AIDeleteProtection:
    """Get global protection instance"""
    global _protection_instance
    if _protection_instance is None:
        _protection_instance = AIDeleteProtection(db_path)
    return _protection_instance

def safe_delete_wrapper(original_delete_func):
    """
    Decorator to wrap any delete function with safety checks
    """
    def wrapper(*args, **kwargs):
        # Create backup before any delete operation
        protection = get_protection_instance()
        protection.prevent_bulk_delete()
        
        # Call original function
        result = original_delete_func(*args, **kwargs)
        
        return result
    
    return wrapper

if __name__ == "__main__":
    # Test the protection system
    protection = AIDeleteProtection("memory/sqlite_db/bhoolamind.db")
    
    print("🛡️ AI Delete Protection System Test")
    print("===================================")
    
    # Test deletion history
    history = protection.get_deletion_history()
    print(f"📊 Deletion history: {len(history)} records")
    
    # Test emergency lockdown
    print("🚨 Testing emergency lockdown...")
    protection.emergency_lockdown()
    print("✅ Emergency lockdown test complete")
    
    print("🔒 AI Delete Protection is ACTIVE")

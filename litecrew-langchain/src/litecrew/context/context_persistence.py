"""
Context Persistence

Optional persistence layer for context data across crew executions.
Supports saving and loading context stores for multi-session workflows.
"""

import os
import pickle
import json
import gzip
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from .shared_context import SharedContextStore, ContextMetadata
from .context_config import ContextConfig


class ContextPersistence:
    """
    Handles persistence of context data to disk.
    
    Provides save/load functionality for SharedContextStore instances
    with compression and cleanup capabilities.
    """
    
    def __init__(self, 
                 storage_dir: str = ".litecrew_context",
                 config: Optional[ContextConfig] = None):
        """
        Initialize context persistence.
        
        Args:
            storage_dir: Directory to store context files
            config: Context configuration
        """
        self.storage_dir = Path(storage_dir)
        self.config = config or ContextConfig()
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Persistence stats
        self._stats = {
            'saves': 0,
            'loads': 0,
            'cleanups': 0,
            'errors': 0,
            'total_size_saved': 0,
            'total_size_loaded': 0
        }
    
    def save_crew_context(self, 
                         crew_id: str, 
                         context_store: SharedContextStore,
                         compress: bool = True) -> bool:
        """
        Save crew context to disk.
        
        Args:
            crew_id: Unique identifier for the crew
            context_store: Context store to save
            compress: Whether to compress the saved data
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{crew_id}_{timestamp}.ctx"
            if compress:
                filename += ".gz"
            
            filepath = self.storage_dir / filename
            
            # Prepare data for serialization
            save_data = {
                'crew_id': crew_id,
                'timestamp': datetime.now().isoformat(),
                'config': {
                    'max_size_mb': context_store.config.max_size_mb,
                    'max_size_per_task': context_store.config.max_size_per_task,
                    'ttl_seconds': context_store.config.ttl_seconds
                },
                'contexts': {},
                'metadata': {},
                'agent_contexts': context_store._agent_contexts,
                'current_size': context_store._current_size,
                'metrics': context_store._metrics
            }
            
            # Serialize contexts and metadata
            context_store._acquire_lock()
            try:
                # Only save non-expired contexts
                for key, value in context_store._contexts.items():
                    metadata = context_store._metadata.get(key)
                    if metadata and not metadata.is_expired():
                        # Convert value to serializable format
                        try:
                            serializable_value = str(value)
                        except:
                            serializable_value = repr(value)
                        
                        save_data['contexts'][key] = serializable_value
                        
                        # Convert metadata to dict
                        save_data['metadata'][key] = {
                            'item_id': metadata.item_id,
                            'agent_role': metadata.agent_role,
                            'task_description': metadata.task_description,
                            'timestamp': metadata.timestamp.isoformat(),
                            'access_count': metadata.access_count,
                            'last_accessed': metadata.last_accessed.isoformat(),
                            'size_bytes': metadata.size_bytes,
                            'priority': metadata.priority,
                            'compressed': metadata.compressed,
                            'ttl_seconds': metadata.ttl_seconds
                        }
            finally:
                context_store._release_lock()
            
            # Save to file
            if compress:
                with gzip.open(filepath, 'wb') as f:
                    pickle.dump(save_data, f)
            else:
                with open(filepath, 'wb') as f:
                    pickle.dump(save_data, f)
            
            # Update stats
            file_size = filepath.stat().st_size
            self._stats['saves'] += 1
            self._stats['total_size_saved'] += file_size
            
            return True
            
        except Exception as e:
            self._stats['errors'] += 1
            print(f"Error saving context for crew {crew_id}: {e}")
            return False
    
    def load_crew_context(self, 
                         crew_id: str,
                         max_age_hours: Optional[int] = None) -> Optional[SharedContextStore]:
        """
        Load crew context from disk.
        
        Args:
            crew_id: Unique identifier for the crew
            max_age_hours: Maximum age of context files to consider
            
        Returns:
            SharedContextStore instance or None if not found
        """
        try:
            # Find most recent context file for this crew
            context_files = []
            for filepath in self.storage_dir.glob(f"{crew_id}_*.ctx*"):
                stat = filepath.stat()
                context_files.append((filepath, stat.st_mtime))
            
            if not context_files:
                return None
            
            # Sort by modification time (newest first)
            context_files.sort(key=lambda x: x[1], reverse=True)
            
            # Check age if specified
            if max_age_hours:
                cutoff_time = time.time() - (max_age_hours * 3600)
                context_files = [(f, t) for f, t in context_files if t >= cutoff_time]
                
                if not context_files:
                    return None
            
            # Load the most recent file
            filepath, _ = context_files[0]
            
            # Determine if compressed
            compressed = str(filepath).endswith('.gz')
            
            # Load data
            if compressed:
                with gzip.open(filepath, 'rb') as f:
                    save_data = pickle.load(f)
            else:
                with open(filepath, 'rb') as f:
                    save_data = pickle.load(f)
            
            # Recreate context store
            loaded_config = ContextConfig()
            if 'config' in save_data:
                config_data = save_data['config']
                loaded_config.max_size_mb = config_data.get('max_size_mb', 10)
                loaded_config.max_size_per_task = config_data.get('max_size_per_task', 10240)
                loaded_config.ttl_seconds = config_data.get('ttl_seconds', 3600)
            
            context_store = SharedContextStore(config=loaded_config)
            
            # Restore contexts and metadata
            context_store._acquire_lock()
            try:
                # Restore contexts
                for key, value in save_data.get('contexts', {}).items():
                    context_store._contexts[key] = value
                
                # Restore metadata
                for key, metadata_dict in save_data.get('metadata', {}).items():
                    metadata = ContextMetadata()
                    metadata.item_id = metadata_dict.get('item_id', metadata.item_id)
                    metadata.agent_role = metadata_dict.get('agent_role')
                    metadata.task_description = metadata_dict.get('task_description')
                    
                    # Parse timestamps
                    try:
                        metadata.timestamp = datetime.fromisoformat(metadata_dict['timestamp'])
                    except:
                        metadata.timestamp = datetime.now()
                    
                    try:
                        metadata.last_accessed = datetime.fromisoformat(metadata_dict['last_accessed'])
                    except:
                        metadata.last_accessed = datetime.now()
                    
                    metadata.access_count = metadata_dict.get('access_count', 0)
                    metadata.size_bytes = metadata_dict.get('size_bytes', 0)
                    metadata.priority = metadata_dict.get('priority', 1)
                    metadata.compressed = metadata_dict.get('compressed', False)
                    metadata.ttl_seconds = metadata_dict.get('ttl_seconds')
                    
                    context_store._metadata[key] = metadata
                
                # Restore agent contexts
                context_store._agent_contexts = save_data.get('agent_contexts', {})
                
                # Restore size and metrics
                context_store._current_size = save_data.get('current_size', 0)
                context_store._metrics.update(save_data.get('metrics', {}))
                
            finally:
                context_store._release_lock()
            
            # Update stats
            file_size = filepath.stat().st_size
            self._stats['loads'] += 1
            self._stats['total_size_loaded'] += file_size
            
            return context_store
            
        except Exception as e:
            self._stats['errors'] += 1
            print(f"Error loading context for crew {crew_id}: {e}")
            return None
    
    def cleanup_old_contexts(self, max_age_hours: int = 24) -> int:
        """
        Clean up old context files.
        
        Args:
            max_age_hours: Maximum age of files to keep
            
        Returns:
            Number of files deleted
        """
        try:
            cutoff_time = time.time() - (max_age_hours * 3600)
            deleted_count = 0
            
            for filepath in self.storage_dir.glob("*.ctx*"):
                stat = filepath.stat()
                if stat.st_mtime < cutoff_time:
                    try:
                        filepath.unlink()
                        deleted_count += 1
                    except:
                        pass
            
            self._stats['cleanups'] += 1
            return deleted_count
            
        except Exception as e:
            self._stats['errors'] += 1
            print(f"Error during cleanup: {e}")
            return 0
    
    def list_saved_contexts(self) -> List[Dict[str, Any]]:
        """
        List all saved context files.
        
        Returns:
            List of context file information
        """
        context_files = []
        
        try:
            for filepath in self.storage_dir.glob("*.ctx*"):
                stat = filepath.stat()
                
                # Parse filename to extract crew_id and timestamp
                filename = filepath.stem.replace('.ctx', '')
                if filename.endswith('.ctx'):
                    filename = filename[:-4]
                
                parts = filename.split('_')
                if len(parts) >= 2:
                    crew_id = '_'.join(parts[:-1])
                    timestamp_str = parts[-1]
                else:
                    crew_id = filename
                    timestamp_str = ""
                
                # Convert timestamp
                try:
                    if timestamp_str:
                        file_timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    else:
                        file_timestamp = datetime.fromtimestamp(stat.st_mtime)
                except:
                    file_timestamp = datetime.fromtimestamp(stat.st_mtime)
                
                context_files.append({
                    'crew_id': crew_id,
                    'filepath': str(filepath),
                    'timestamp': file_timestamp.isoformat(),
                    'size_bytes': stat.st_size,
                    'compressed': str(filepath).endswith('.gz')
                })
        
        except Exception as e:
            print(f"Error listing contexts: {e}")
        
        # Sort by timestamp (newest first)
        context_files.sort(key=lambda x: x['timestamp'], reverse=True)
        return context_files
    
    def delete_crew_contexts(self, crew_id: str) -> int:
        """
        Delete all context files for a specific crew.
        
        Args:
            crew_id: Crew identifier
            
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        
        try:
            for filepath in self.storage_dir.glob(f"{crew_id}_*.ctx*"):
                try:
                    filepath.unlink()
                    deleted_count += 1
                except:
                    pass
        
        except Exception as e:
            print(f"Error deleting contexts for crew {crew_id}: {e}")
        
        return deleted_count
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = self._stats.copy()
        
        # Add directory stats
        try:
            total_files = len(list(self.storage_dir.glob("*.ctx*")))
            total_size = sum(f.stat().st_size for f in self.storage_dir.glob("*.ctx*"))
            
            stats.update({
                'storage_directory': str(self.storage_dir),
                'total_files': total_files,
                'total_storage_size_bytes': total_size,
                'total_storage_size_mb': total_size / (1024 * 1024)
            })
        except:
            stats.update({
                'storage_directory': str(self.storage_dir),
                'total_files': 0,
                'total_storage_size_bytes': 0,
                'total_storage_size_mb': 0
            })
        
        return stats
    
    def export_context_json(self, crew_id: str, output_file: str) -> bool:
        """
        Export context to JSON format for external analysis.
        
        Args:
            crew_id: Crew identifier
            output_file: Output JSON file path
            
        Returns:
            bool: True if exported successfully
        """
        try:
            context_store = self.load_crew_context(crew_id)
            if not context_store:
                return False
            
            # Prepare JSON data
            export_data = {
                'crew_id': crew_id,
                'export_timestamp': datetime.now().isoformat(),
                'contexts': {},
                'metadata': {},
                'metrics': context_store.get_metrics(),
                'agent_contexts': context_store._agent_contexts
            }
            
            # Export contexts
            context_store._acquire_lock()
            try:
                for key, value in context_store._contexts.items():
                    metadata = context_store._metadata.get(key)
                    if metadata:
                        export_data['contexts'][key] = str(value)
                        export_data['metadata'][key] = {
                            'agent_role': metadata.agent_role,
                            'task_description': metadata.task_description,
                            'timestamp': metadata.timestamp.isoformat(),
                            'access_count': metadata.access_count,
                            'size_bytes': metadata.size_bytes,
                            'priority': metadata.priority
                        }
            finally:
                context_store._release_lock()
            
            # Save JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting context to JSON: {e}")
            return False
"""
Cache management module for storing and retrieving analysis results and embeddings.
"""
from pathlib import Path
import json
import pickle
import hashlib
from datetime import datetime, timedelta
import shutil
from typing import Any, Optional, Dict, Union
from loguru import logger
from app.core.config import settings

class AnalysisCache:
    def __init__(self, cache_dir: Union[str, Path] = None):
        self.cache_dir = Path(cache_dir or settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._init_cache_structure()
        
    def _init_cache_structure(self):
        """Initialize the cache directory structure."""
        (self.cache_dir / "metadata").mkdir(exist_ok=True)
        (self.cache_dir / "embeddings").mkdir(exist_ok=True)
        (self.cache_dir / "analysis").mkdir(exist_ok=True)
        
    def _compute_cache_key(self, content: Union[str, bytes], prefix: str = "") -> str:
        """
        Compute a unique cache key for the given content.
        """
        if isinstance(content, str):
            content = content.encode('utf-8')
        hash_obj = hashlib.sha256(content)
        return f"{prefix}_{hash_obj.hexdigest()}" if prefix else hash_obj.hexdigest()
    
    def _get_cache_path(self, cache_key: str, cache_type: str) -> Path:
        """
        Get the full path for a cache item.
        """
        return self.cache_dir / cache_type / cache_key
    
    def store(self, key: str, data: Any, cache_type: str, metadata: Optional[Dict] = None) -> bool:
        """
        Store data in the cache with optional metadata.
        """
        try:
            cache_path = self._get_cache_path(key, cache_type)
            
            # Store the actual data
            if isinstance(data, (dict, list)):
                with cache_path.with_suffix('.json').open('w', encoding='utf-8') as f:
                    json.dump(data, f)
            else:
                with cache_path.with_suffix('.pkl').open('wb') as f:
                    pickle.dump(data, f)
            
            # Store metadata if provided
            if metadata:
                metadata.update({
                    'created_at': datetime.now().isoformat(),
                    'cache_type': cache_type
                })
                meta_path = self._get_cache_path(key, 'metadata')
                with meta_path.with_suffix('.json').open('w', encoding='utf-8') as f:
                    json.dump(metadata, f)
                    
            return True
            
        except Exception as e:
            logger.error(f"Error storing cache item {key}: {str(e)}")
            return False
    
    def retrieve(self, key: str, cache_type: str) -> Optional[Any]:
        """
        Retrieve data from the cache.
        """
        try:
            cache_path = self._get_cache_path(key, cache_type)
            
            # Check for JSON data
            json_path = cache_path.with_suffix('.json')
            if json_path.exists():
                with json_path.open('r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Check for pickle data
            pkl_path = cache_path.with_suffix('.pkl')
            if pkl_path.exists():
                with pkl_path.open('rb') as f:
                    return pickle.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cache item {key}: {str(e)}")
            return None
    
    def get_metadata(self, key: str) -> Optional[Dict]:
        """
        Retrieve metadata for a cache item.
        """
        try:
            meta_path = self._get_cache_path(key, 'metadata').with_suffix('.json')
            if meta_path.exists():
                with meta_path.open('r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error retrieving metadata for {key}: {str(e)}")
            return None
    
    def is_valid(self, key: str, max_age: Optional[timedelta] = None) -> bool:
        """
        Check if a cache item is valid based on its age.
        """
        metadata = self.get_metadata(key)
        if not metadata or 'created_at' not in metadata:
            return False
            
        if max_age:
            created_at = datetime.fromisoformat(metadata['created_at'])
            return datetime.now() - created_at <= max_age
            
        return True
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate a cache item and its metadata.
        """
        try:
            # Remove all possible cache files for the key
            for cache_type in ['metadata', 'embeddings', 'analysis']:
                cache_path = self._get_cache_path(key, cache_type)
                for ext in ['.json', '.pkl']:
                    file_path = cache_path.with_suffix(ext)
                    if file_path.exists():
                        file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache item {key}: {str(e)}")
            return False
    
    def clear(self, cache_type: Optional[str] = None) -> bool:
        """
        Clear all cache data or specific cache type.
        """
        try:
            if cache_type:
                cache_path = self.cache_dir / cache_type
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                    cache_path.mkdir()
            else:
                shutil.rmtree(self.cache_dir)
                self._init_cache_structure()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def get_cache_size(self, cache_type: Optional[str] = None) -> int:
        """
        Get the total size of cache in bytes.
        """
        total_size = 0
        if cache_type:
            cache_path = self.cache_dir / cache_type
            if cache_path.exists():
                total_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
        else:
            total_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*') if f.is_file())
        return total_size
    
    def cleanup(self, max_age: timedelta, max_size: int = None) -> bool:
        """
        Clean up old cache entries and ensure cache doesn't exceed max size.
        """
        try:
            # Remove old entries
            now = datetime.now()
            for meta_file in (self.cache_dir / 'metadata').glob('*.json'):
                with meta_file.open('r', encoding='utf-8') as f:
                    metadata = json.load(f)
                created_at = datetime.fromisoformat(metadata['created_at'])
                if now - created_at > max_age:
                    self.invalidate(meta_file.stem)
            
            # Check total size if max_size is specified
            if max_size:
                current_size = self.get_cache_size()
                if current_size > max_size:
                    # Remove oldest entries until size is under limit
                    cache_files = []
                    for meta_file in (self.cache_dir / 'metadata').glob('*.json'):
                        with meta_file.open('r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        cache_files.append((
                            meta_file.stem,
                            datetime.fromisoformat(metadata['created_at'])
                        ))
                    
                    # Sort by creation time and remove oldest
                    cache_files.sort(key=lambda x: x[1])
                    while current_size > max_size and cache_files:
                        key, _ = cache_files.pop(0)
                        self.invalidate(key)
                        current_size = self.get_cache_size()
            
            return True
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {str(e)}")
            return False

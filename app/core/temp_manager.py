"""
Temporary file management module for handling uploaded documents and intermediate processing files.
"""
from pathlib import Path
import tempfile
import shutil
import os
from datetime import datetime, timedelta
from typing import Optional, List, Union
from loguru import logger
import magic
from app.core.config import settings

class TempFileManager:
    def __init__(self, base_dir: Union[str, Path] = None, max_age: timedelta = timedelta(hours=24)):
        """
        Initialize the temporary file manager.
        
        Args:
            base_dir: Base directory for temporary files. If None, uses system temp directory
            max_age: Maximum age of temporary files before cleanup
        """
        self.base_dir = Path(base_dir) if base_dir else Path(tempfile.gettempdir()) / "rag_analyzer"
        self.max_age = max_age
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._init_temp_structure()
        
    def _init_temp_structure(self):
        """Initialize the temporary directory structure."""
        (self.base_dir / "uploads").mkdir(exist_ok=True)
        (self.base_dir / "processing").mkdir(exist_ok=True)
        (self.base_dir / "exports").mkdir(exist_ok=True)
        
    def create_temp_dir(self, prefix: str = "") -> Path:
        """
        Create a new temporary directory.
        
        Args:
            prefix: Optional prefix for the directory name
        
        Returns:
            Path to the created temporary directory
        """
        temp_dir = self.base_dir / "processing" / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> Path:
        """
        Save an uploaded file to the temporary directory.
        
        Args:
            file_content: The content of the uploaded file
            original_filename: Original name of the uploaded file
        
        Returns:
            Path to the saved temporary file
        """
        try:
            # Detect file type using python-magic
            mime_type = magic.from_buffer(file_content, mime=True)
            
            # Validate file type
            if not self._is_valid_file_type(mime_type):
                raise ValueError(f"Unsupported file type: {mime_type}")
            
            # Create safe filename
            safe_filename = self._create_safe_filename(original_filename)
            temp_path = self.base_dir / "uploads" / safe_filename
            
            # Save file
            with temp_path.open("wb") as f:
                f.write(file_content)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error saving uploaded file {original_filename}: {str(e)}")
            raise
    
    def _is_valid_file_type(self, mime_type: str) -> bool:
        """
        Check if the file type is supported.
        """
        valid_types = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain'
        }
        return mime_type in valid_types
    
    def _create_safe_filename(self, filename: str) -> str:
        """
        Create a safe version of the filename.
        """
        # Remove potentially dangerous characters
        safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ")
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{safe_name}"
    
    def create_temp_file(self, prefix: str = "", suffix: str = "") -> Path:
        """
        Create a new temporary file.
        
        Args:
            prefix: Optional prefix for the filename
            suffix: Optional suffix (extension) for the filename
        
        Returns:
            Path to the created temporary file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}{suffix}" if prefix else f"temp_{timestamp}{suffix}"
        temp_path = self.base_dir / "processing" / filename
        temp_path.touch()
        return temp_path
    
    def cleanup_old_files(self, max_age: Optional[timedelta] = None) -> List[Path]:
        """
        Remove temporary files older than max_age.
        
        Args:
            max_age: Maximum age of files to keep. If None, uses instance default
        
        Returns:
            List of removed file paths
        """
        max_age = max_age or self.max_age
        removed_files = []
        now = datetime.now()
        
        try:
            for temp_dir in [self.base_dir / d for d in ["uploads", "processing", "exports"]]:
                for file_path in temp_dir.glob("*"):
                    if file_path.is_file():
                        file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if now - file_age > max_age:
                            file_path.unlink()
                            removed_files.append(file_path)
                            
            return removed_files
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return removed_files
    
    def get_temp_file_info(self, file_path: Union[str, Path]) -> dict:
        """
        Get information about a temporary file.
        
        Args:
            file_path: Path to the temporary file
        
        Returns:
            Dictionary containing file information
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "mime_type": magic.from_file(str(path), mime=True)
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            raise
    
    def move_to_exports(self, file_path: Union[str, Path], new_name: Optional[str] = None) -> Path:
        """
        Move a temporary file to the exports directory.
        
        Args:
            file_path: Path to the temporary file
            new_name: Optional new name for the exported file
        
        Returns:
            Path to the exported file
        """
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
            
        try:
            if new_name:
                target_path = self.base_dir / "exports" / new_name
            else:
                target_path = self.base_dir / "exports" / source_path.name
                
            shutil.move(str(source_path), str(target_path))
            return target_path
            
        except Exception as e:
            logger.error(f"Error moving file to exports: {str(e)}")
            raise
    
    def clear_temp_files(self, subdir: Optional[str] = None) -> bool:
        """
        Clear all temporary files in the specified subdirectory or all directories.
        
        Args:
            subdir: Optional subdirectory to clear ("uploads", "processing", or "exports")
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if subdir:
                temp_dir = self.base_dir / subdir
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    temp_dir.mkdir()
            else:
                shutil.rmtree(self.base_dir)
                self.base_dir.mkdir()
                self._init_temp_structure()
            return True
        except Exception as e:
            logger.error(f"Error clearing temporary files: {str(e)}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        try:
            self.cleanup_old_files()
        except Exception as e:
            logger.error(f"Error during context manager cleanup: {str(e)}")
            
    def get_storage_stats(self) -> dict:
        """
        Get storage statistics for temporary files.
        
        Returns:
            Dictionary containing storage statistics
        """
        stats = {
            "total_size": 0,
            "file_count": 0,
            "by_type": {
                "uploads": {"size": 0, "count": 0},
                "processing": {"size": 0, "count": 0},
                "exports": {"size": 0, "count": 0}
            }
        }
        
        try:
            for subdir in ["uploads", "processing", "exports"]:
                dir_path = self.base_dir / subdir
                if dir_path.exists():
                    for file_path in dir_path.glob("*"):
                        if file_path.is_file():
                            size = file_path.stat().st_size
                            stats["by_type"][subdir]["size"] += size
                            stats["by_type"][subdir]["count"] += 1
                            stats["total_size"] += size
                            stats["file_count"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return stats

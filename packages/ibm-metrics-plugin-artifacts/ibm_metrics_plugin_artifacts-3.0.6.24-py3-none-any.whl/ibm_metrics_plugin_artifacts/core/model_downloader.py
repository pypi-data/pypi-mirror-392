# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2024  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import os
import shutil
import threading
import time
from pathlib import Path
from sentence_transformers import SentenceTransformer


class ModelDownloader:
    """
    Handles downloading and caching of sentence transformer models.
    Models are downloaded from HuggingFace on first use and cached locally.
    Thread-safe implementation ensures only one download per model across multiple threads.
    """
    
    # Map internal model names to HuggingFace model identifiers
    MODEL_MAPPING = {
        "sentence-transformers/all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/bert-based-multilingual-cased": "bert-base-multilingual-cased"
    }
    
    # Class-level lock dictionary for thread synchronization
    _download_locks = {}
    _locks_lock = threading.Lock()
    
    def __init__(self):
        """Initialize the model downloader with cache directory."""
        self.cache_dir = self._get_cache_dir()
        
    def _get_cache_dir(self):
        """Get or create the cache directory for models."""
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))
        cache_dir = os.path.join(base_path, 'artifacts', 'models', 'sentence-transformers')
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    
    def _get_model_cache_path(self, model_name):
        """Get the local cache path for a specific model."""
        # Extract just the model name (e.g., "all-MiniLM-L6-v2" from full path)
        model_short_name = model_name.split('/')[-1]
        return os.path.join(self.cache_dir, model_short_name)
    
    def _get_model_lock(self, model_name):
        """
        Get or create a lock for a specific model to ensure thread-safe downloads.
        
        Args:
            model_name: The model name to get a lock for
            
        Returns:
            threading.Lock object for the specified model
        """
        with self._locks_lock:
            if model_name not in self._download_locks:
                self._download_locks[model_name] = threading.Lock()
            return self._download_locks[model_name]
    
    def _is_model_cached(self, model_name):
        """Check if model is already downloaded and cached."""
        cache_path = self._get_model_cache_path(model_name)
        # Check if directory exists and contains model files
        if os.path.exists(cache_path):
            # Verify it has essential model files
            required_files = ['config.json']
            has_model_file = (
                os.path.exists(os.path.join(cache_path, 'model.safetensors')) or
                os.path.exists(os.path.join(cache_path, 'pytorch_model.bin'))
            )
            has_required = all(
                os.path.exists(os.path.join(cache_path, f)) for f in required_files
            )
            return has_required and has_model_file
        return False
    
    def _wait_for_download_completion(self, cache_path, timeout=300):
        """
        Wait for another thread to complete downloading the model.
        
        Args:
            cache_path: Path where the model should be cached
            timeout: Maximum time to wait in seconds (default: 5 minutes)
            
        Returns:
            True if model is now available, False if timeout occurred
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._is_model_cached(os.path.basename(cache_path)):
                return True
            time.sleep(1)  # Check every second
        return False
    
    def download_model(self, model_name, force_download=False):
        """
        Download a model from HuggingFace if not already cached.
        Thread-safe: Only one thread will download while others wait.
        
        Args:
            model_name: Internal model name (e.g., "sentence-transformers/all-MiniLM-L6-v2")
            force_download: If True, re-download even if cached
            
        Returns:
            Path to the cached model directory
        """
        cache_path = self._get_model_cache_path(model_name)
        
        # Quick check without lock - if model is cached and not forcing download
        if not force_download and self._is_model_cached(model_name):
            print(f"Model '{model_name}' found in cache: {cache_path}")
            return cache_path
        
        # Get model-specific lock to ensure only one thread downloads
        model_lock = self._get_model_lock(model_name)
        
        # Try to acquire the lock
        lock_acquired = model_lock.acquire(blocking=False)
        
        if lock_acquired:
            try:
                # Double-check if model is cached (another thread might have downloaded it)
                if not force_download and self._is_model_cached(model_name):
                    print(f"Model '{model_name}' found in cache: {cache_path}")
                    return cache_path
                
                # Get HuggingFace model identifier
                hf_model_name = self.MODEL_MAPPING.get(model_name, model_name)
                
                print(f"Downloading model '{hf_model_name}' from HuggingFace...")
                print(f"This may take a few minutes on first use...")
                
                # Download model using sentence-transformers
                # This will use HuggingFace's cache first, then download if needed
                model = SentenceTransformer(hf_model_name)
                
                # Save to our local cache directory
                if os.path.exists(cache_path):
                    shutil.rmtree(cache_path)
                
                model.save(cache_path)
                print(f"Model successfully cached at: {cache_path}")
                
                return cache_path
                
            except Exception as e:
                print(f"Error downloading model '{model_name}': {str(e)}")
                raise
            finally:
                model_lock.release()
        else:
            # Another thread is downloading, wait for it to complete
            print(f"Another thread is downloading model '{model_name}', waiting...")
            
            # Wait for the lock to be released (download to complete)
            with model_lock:
                # Once we acquire the lock, the download should be complete
                if self._is_model_cached(model_name):
                    print(f"Model '{model_name}' download completed by another thread: {cache_path}")
                    return cache_path
                else:
                    # If still not cached, something went wrong with the other thread
                    # Try downloading ourselves
                    print(f"Model '{model_name}' not found after waiting, attempting download...")
                    return self.download_model(model_name, force_download=force_download)
    
    def get_model_path(self, model_name):
        """
        Get the path to a model, downloading it if necessary.
        
        Args:
            model_name: Internal model name
            
        Returns:
            Path to the model directory
        """
        return self.download_model(model_name, force_download=False)



# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2024  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import os
from sentence_transformers import SentenceTransformer
from .model_downloader import ModelDownloader


class LoadArtifacts:

    def __init__(self):
        """Initialize LoadArtifacts with model downloader."""
        self.model_downloader = ModelDownloader()

    def load_dataset(self, dataset_name):

        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))

        # Construct the path to the dataset
        dataset_path = os.path.join(
            base_path, 'artifacts', 'datasets', dataset_name)

        # Read the JSON file
        with open(dataset_path, 'rb') as file:
            dataset = file.read()

        return dataset

    def load_model(self, model_name):
        """
        Load a sentence transformer model.
        
        Args:
            model_name: Model name (e.g., "sentence-transformers/all-MiniLM-L6-v2")
        
        Returns:
            SentenceTransformer model instance
        """
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))

        # Construct the path to the model
        model_path = os.path.join(
            base_path, 'artifacts', 'models', model_name)

        # Check if model exists locally (bundled in package)
        if os.path.exists(model_path) and os.path.isdir(model_path):
            # Check if it has model files
            has_model = (
                os.path.exists(os.path.join(model_path, 'config.json')) and
                (os.path.exists(os.path.join(model_path, 'model.safetensors')) or
                 os.path.exists(os.path.join(model_path, 'pytorch_model.bin')))
            )
            if has_model:
                model = SentenceTransformer(model_path)
                return model
        
        # Model not bundled, download it
        print(f"Model not found locally, downloading: {model_name}")
        model_path = self.model_downloader.get_model_path(model_name)
        model = SentenceTransformer(model_path)
        return model

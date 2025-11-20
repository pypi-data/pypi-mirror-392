from balinese_nlp.embeddings.BasePretrained import BasePretrained
from huggingface_hub import hf_hub_download
import pickle


class BaliTFISF(BasePretrained):
    def __init__(self, huggingface_repo_ID, pretrained_model_name="tfisf_1gram.pkl"):
        super().__init__(
            huggingface_repo_ID=huggingface_repo_ID
        )
        self.filepath_pretrained_model_pkl = f"TFISF/{pretrained_model_name}"

    def load_pretrained_model(self):
        super().load_pretrained_model()
        repo_id = self.repo_id

        # download the .pkl file into local disk
        tfisf_pkl_filename = self.filepath_pretrained_model_pkl
        print(f"Downloading {tfisf_pkl_filename} from {repo_id}...")
        local_bin_path_tfisf = hf_hub_download(
            repo_id=repo_id,
            filename=tfisf_pkl_filename,
            revision='master'
        )
        print(f"Downloaded to: {local_bin_path_tfisf}")

        # retrieve the pretrained model
        self.pretrained_model = pickle.load(open(local_bin_path_tfisf, 'rb'))

        return self.pretrained_model

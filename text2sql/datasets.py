from data_models import Sample, SpiderSample
from utils import load_data, SpiderUtils
from tqdm import tqdm
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Dataset:
    samples: list[Sample]
    _raw_samples: list[dict]
    _dataset_dir: str
    _file_name: str

    def __init__(self, dataset_dir: str, file_name: str):
        self._raw_samples = load_data(dataset_dir, file_name)
        self._dataset_dir = dataset_dir
        self._file_name = file_name

    def _get_dbs_info(self, db_path: str = "database"):
        pass

    def _get_samples(self):
        pass


class SpiderDataset(Dataset):
    _path_to_gold: str
    _table_file_path: str
    _path_to_db: str  # ???
    dbs_info: dict
    samples: list[SpiderSample]
    # _path_to_schema_linking ???

    def __init__(
        self,
        dataset_dir: str,
        file_name: str,
        path_to_gold: str,
        is_test: bool = False,
        table_file_path: str = None,
    ):
        super().__init__(dataset_dir, file_name)
        self._table_file_path = table_file_path
        self._path_to_gold = path_to_gold
        self.is_test = is_test
        self.dbs_info = self._get_dbs_info()

        self.samples = self._get_samples()

    # override _get_dbs_info
    def _get_dbs_info(self, db_path: str = "database"):
        if not self._table_file_path:
            return super()._get_dbs_info(db_path)
        else:
            data = load_data(self._dataset_dir, self._table_file_path)
            return SpiderUtils.parse_tables(data)

    def _get_samples(self):
        samples = []
        gold_raw = SpiderUtils.get_gold_queries(
            os.path.join(PROJECT_ROOT, "data", self._dataset_dir, self._path_to_gold),
            self.is_test,
        )

        for raw_sample, gold_q in tqdm(
            zip(self._raw_samples, gold_raw), desc="Processing samples"
        ):
            samples.append(
                SpiderSample(
                    raw_sample
                    | {"db_info": self.dbs_info.get(raw_sample["db_id"], {})}
                    | {"query_gold": gold_q}
                )
            )

        return samples


if __name__ == "__main__":
    print(PROJECT_ROOT)
    # Test Dataset
    dataset = SpiderDataset(
        "spider_data",
        "dev.json",
        "dev_gold.sql",
        table_file_path="tables.json",
        is_test=True,
    )
    print(dataset.samples[0].question)
    print(dataset.samples[0].query)
    print(dataset.samples[0].query_gold)

import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_data(dataset_dir: str, file_name: str) -> list[dict]:
    file_path = os.path.join(PROJECT_ROOT, "data", dataset_dir, file_name)
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"File not found: {file_path}\
                                \nPlease check the location of dataset and file name"
        )
    return data


class SpiderUtils:
    @staticmethod
    def get_hardness():
        # https://github.com/taoyds/spider/blob/master/evaluation.py#L303 - todo
        pass

    @staticmethod
    def get_schema():
        pass

    @staticmethod
    def parse_tables(data: list) -> dict[str, list[dict[str, list]]]:
        """
        Parse tables.json into a dictionary mapping database IDs to their schema information.

        Args:
            tables_json: Path to tables.json file

        Returns:
            Dict mapping database IDs to list of tables and their columns
        {
            'db_id': [
                {'table_name': [
                    {
                        'name': column_name,
                        'type': column_type,
                        'primary': boolean,
                        'foreign': foreign_key_reference
                    }
                ]},
                ...
            ]
        }
        """
        schema_dict = {}

        for db in data:
            db_id = db["db_id"]
            schema_dict[db_id] = []

            # Process each table in the database
            for idx, table in enumerate(db["table_names"]):
                table_dict = {table: []}

                # Process columns for this table
                for col_idx, (table_id, col_name) in enumerate(db["column_names"]):
                    if table_id == idx:  # Column belongs to current table
                        col_info = {
                            "name": col_name,
                            "type": db["column_types"][col_idx],
                            "primary": col_idx in db["primary_keys"],
                            "foreign": None,
                        }

                        # Check if column is a foreign key
                        for fk_pair in db["foreign_keys"]:
                            if col_idx == fk_pair[0]:
                                ref_col = db["column_names"][fk_pair[1]][1]
                                ref_table = db["table_names"][
                                    db["column_names"][fk_pair[1]][0]
                                ]
                                col_info["foreign"] = f"{ref_table}.{ref_col}"

                        table_dict[table].append(col_info)

                schema_dict[db_id].append(table_dict)

        return schema_dict

    @staticmethod
    def get_gold_queries(file_path: str) -> list[list[str]]:
        """Extract SQL queries from Spider gold SQL files.

        Args:
            file_path: Path to the .sql file
            is_test: If True, store pairs of queries for each example. If False, store single queries.

        Returns:
            List of lists of SQL queries. Inner lists contain either 1 or 2 queries depending on is_test.
        """
        queries = []

        with open(file_path, "r") as f:
            for line_number, line in enumerate(f, 1):  # Start counting from 1
                if line.strip() and not line.startswith("--"):
                    parts = line.strip().split("\t")
                    if len(parts) < 2:  # Check for both query and database parts
                        raise ValueError(
                            f"Invalid format in line {line_number}: Expected 'query\\tdatabase', got '{line.strip()}'"
                        )

                    query = parts[0]
                    queries.append(query)

        return queries


if __name__ == "__main__":
    print(PROJECT_ROOT)
    # Test load_data
    # data = load_data("spider_data", "train_spider.json")
    # print(data[0])

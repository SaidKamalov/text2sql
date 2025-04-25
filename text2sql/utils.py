import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_data(dataset_dir: str, file_name: str) -> list[dict]:
    """
    Load JSON data from a specified file in the dataset directory.
    Args:
        dataset_dir: Directory containing the dataset files.
        file_name: Name of the JSON file to load.
    Returns:
        List of dictionaries containing the data from the JSON file.
    """
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
        """
        Extract SQL queries from Spider gold SQL files.
        Args:
            file_path: Path to the .sql file
        Returns:
            List of ground truth (gold) SQL queries.
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


class HardnessEvaluator:
    """
    Reference: https://github.com/taoyds/test-suite-sql-eval/blob/master/evaluation.py#L361
    """

    WHERE_OPS = (
        "not",
        "between",
        "=",
        ">",
        "<",
        ">=",
        "<=",
        "!=",
        "in",
        "like",
        "is",
        "exists",
    )
    AGG_OPS = ("none", "max", "min", "count", "sum", "avg")

    def has_agg(unit):
        return unit[0] != HardnessEvaluator.AGG_OPS.index("none")

    def count_agg(units):
        return len([unit for unit in units if HardnessEvaluator.has_agg(unit)])

    def count_component1(sql):
        count = 0
        if len(sql.get("where", [])) > 0:
            count += 1
        if len(sql.get("groupBy", [])) > 0:
            count += 1
        if len(sql.get("orderBy", [])) > 0:
            count += 1
        if sql.get("limit") is not None:
            count += 1
        if len(sql.get("from", {}).get("table_units", [])) > 0:
            count += len(sql["from"]["table_units"]) - 1
        ao = (
            sql.get("from", {}).get("conds", [])[1::2]
            + sql.get("where", [])[1::2]
            + sql.get("having", [])[1::2]
        )
        count += len([token for token in ao if token == "or"])
        cond_units = (
            sql.get("from", {}).get("conds", [])[::2]
            + sql.get("where", [])[::2]
            + sql.get("having", [])[::2]
        )
        count += len(
            [
                cond_unit
                for cond_unit in cond_units
                if cond_unit[1] == HardnessEvaluator.WHERE_OPS.index("like")
            ]
        )
        return count

    def get_nestedSQL(sql):
        nested = []
        for cond_unit in (
            sql.get("from", {}).get("conds", [])[::2]
            + sql.get("where", [])[::2]
            + sql.get("having", [])[::2]
        ):
            if type(cond_unit[3]) is dict:
                nested.append(cond_unit[3])
            if type(cond_unit[4]) is dict:
                nested.append(cond_unit[4])
        for op in ["intersect", "except", "union"]:
            if sql.get(op) is not None:
                nested.append(sql[op])
        return nested

    def count_component2(sql):
        nested = HardnessEvaluator.get_nestedSQL(sql)
        return len(nested)

    def count_others(sql):
        count = 0
        agg_count = HardnessEvaluator.count_agg(sql.get("select", [None, []])[1])
        agg_count += HardnessEvaluator.count_agg(sql.get("where", [])[::2])
        agg_count += HardnessEvaluator.count_agg(sql.get("groupBy", []))
        if len(sql.get("orderBy", [])) > 0:
            agg_count += HardnessEvaluator.count_agg(
                [unit[1] for unit in sql["orderBy"][1] if unit[1]]
                + [unit[2] for unit in sql["orderBy"][1] if unit[2]]
            )
        agg_count += HardnessEvaluator.count_agg(sql.get("having", []))
        if agg_count > 1:
            count += 1
        if len(sql.get("select", [None, []])[1]) > 1:
            count += 1
        if len(sql.get("where", [])) > 1:
            count += 1
        if len(sql.get("groupBy", [])) > 1:
            count += 1
        return count

    def eval_sql_hardness(sql):
        count_comp1_ = HardnessEvaluator.count_component1(sql)
        count_comp2_ = HardnessEvaluator.count_component2(sql)
        count_others_ = HardnessEvaluator.count_others(sql)
        if count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ == 0:
            return "easy"
        elif (count_others_ <= 2 and count_comp1_ <= 1 and count_comp2_ == 0) or (
            count_comp1_ <= 2 and count_others_ < 2 and count_comp2_ == 0
        ):
            return "medium"
        elif (
            (count_others_ > 2 and count_comp1_ <= 2 and count_comp2_ == 0)
            or (2 < count_comp1_ <= 3 and count_others_ <= 2 and count_comp2_ == 0)
            or (count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ <= 1)
        ):
            return "hard"
        else:
            return "extra"


if __name__ == "__main__":
    pass

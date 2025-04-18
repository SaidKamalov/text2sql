class Sample:
    db_id: str
    question: str
    query: str

    def __init__(self, raw_sample: dict):
        pass


class SpiderSample(Sample):
    id: int

    # Question related fields
    question_toks: list

    # DB related fields
    db_info: dict
    schema: dict  # todo: make schema class???

    # Query related fields
    query_toks: list
    query_toks_no_value: list
    sql_parsed: dict
    hardness: str  # todo: maked enum

    # Eval related fields
    query_gold: list[str]
    sql_parsed_gold: dict

    def __init__(self, raw_sample: dict):
        try:
            self.db_id = raw_sample["db_id"]
            self.question = raw_sample["question"]
            self.query = raw_sample["query"]
        except KeyError as e:
            raise ValueError(
                f"Missing key: {e}\n keys: db_id, question, query - are necessary"
            )

        # TODO: add initialization with specific functions, if necessary info is missing in the file
        self.question_toks = raw_sample.get("question_toks", [])  # +
        self.db_info = raw_sample.get("db_info", {})  # done in SpiderDataset
        self.schema = raw_sample.get("schema", {})  # ???
        self.query_toks = raw_sample.get("query_toks", [])  # +
        self.query_toks_no_value = raw_sample.get("query_toks_no_value", [])  # +
        self.sql_parsed = raw_sample.get("sql", {})  # +
        self.hardness = raw_sample.get("hardness", "")
        self.query_gold = raw_sample.get("query_gold", [])  # done in SpiderDataset +
        self.sql_parsed_gold = raw_sample.get("sql_parsed_gold", {})

    # def set_db_info(self, dbs_info: dict):
    #     self.db_info = dbs_info.get(self.db_id, {})

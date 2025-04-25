from text2sql.data_models import Sample
from text2sql.get_examples import select_k_shot_examples
from text2sql.enums import ExampleSelectionType


class OAIPrompt:
    intro: str = "### Complete sqlite SQL query only and with no explanation.\n"

    def build_prompt(
        sample: Sample,
        k: int,
        examples: list[Sample] = None,
        example_selection_type: ExampleSelectionType = None,
        schema_info_option=None,
        add_fk_info: bool = False,
        add_cv_ref: bool = False,
        op_rule=None,
    ):
        prompt_message = ""
        prompt_message += OAIPrompt.intro
        if op_rule:
            prompt_message += "### " + op_rule + "\n"

        if schema_info_option:
            prompt_message += "### SQLite SQL tables, with their properties:\n#\n"
            schema_info = OAIPrompt._schema_info_prep(sample.db_info)
            prompt_message += schema_info

        if add_fk_info:
            prompt_message += "### Foreign Key References:\n#\n"
            fk_info = OAIPrompt._fk_info_prep(sample.db_info)
            prompt_message += fk_info

        if k > 0 and examples:
            example_message = ""
            examples = select_k_shot_examples(
                sample, k, examples, example_selection_type
            )
            example_message += "### Examples:\n"
            for ex in examples:
                example_message += f"# Question: {ex.question}\n"
                example_message += f"# Answer: {ex.query}\n#\n"
        else:
            example_message = ""
        prompt_message += example_message

        question = "### Question: " + sample.question + "\n### Answer: SELECT"
        prompt_message += question

        return prompt_message

    def _schema_info_prep(db_info, add_cv_ref: bool = False):
        # TODO:
        #   Add option to include only linked tables and columns
        #   Implement cv references
        message = ""
        tables = []
        for table in db_info:
            row = []
            for t_name, columns in table.items():
                for column in columns:
                    col_name = column["name"]
                    row.append(col_name)
                full_row = "# " + f"{t_name}: (" + ", ".join(row) + ")"
                tables.append(full_row)
        message += "\n".join(tables)
        message += "\n#\n"

        return message

    def _fk_info_prep(db_info):
        message = ""
        for table in db_info:
            for t_name, columns in table.items():
                for column in columns:
                    if column["foreign"]:
                        message += f"# {t_name}.{column['name']} references {column['foreign']}\n"
        return message + "#\n"


class ReasoningPrompt:

    def build_prompt(
        sample: Sample,
        k: int,
        examples: list[Sample],
        example_selection_type: ExampleSelectionType = None,
        schema_info_option=None,
        add_fk_info: bool = False,
        add_cv_ref: bool = False,
        op_rule=None,
    ):

        prompt_message = ""
        goal = (
            "## Goal:\n"
            "Your task is to translate any given natural language question into a valid SQL query written in the SQLite dialect.\n"
        )
        if op_rule:
            goal += "*" + op_rule + "*\n"
        prompt_message += goal + "\n"

        return_format = (
            "## Return Format:\n"
            "Write SQLite query only and with no explanation or comments.\n"
            "Do not use any aliases for tables or columns.\n"
            "Return only SQLite query in a format: SELECT ...\n\n"
        )

        prompt_message += return_format

        warnings = (
            "## Warnings:\n"
            "**Be careful and double-check:**\n"
            "1. The correctness of SQLite syntax and order of operations and closes.\n"
            "2. The choice of columns and tables when dealing with ambiguity of natural language\n"
            "3. The correctness of the join conditions if it is used.\n\n"
        )

        prompt_message += warnings

        schema_info, fk_info = "", ""
        if schema_info_option:
            schema_message = "**SQLite SQL tables, with their properties:**\n\n"
            schema_info += schema_message + ReasoningPrompt._schema_info_prep(
                sample.db_info
            )

        if add_fk_info:
            fk_message = "**Foreign Key References:**\n\n"
            fk_info += fk_message + ReasoningPrompt._fk_info_prep(sample.db_info)

        context = f"## Context:\n{schema_info}{fk_info}"

        if schema_info_option or add_fk_info:
            prompt_message += context

        if k > 0 and examples:
            example_message = ""
            examples = select_k_shot_examples(
                sample, k, examples, example_selection_type
            )
            example_message += "## Examples:\n"
            for ex in examples:
                example_message += f"**Question:** {ex.question}\n"
                example_message += f"**Answer:** {ex.query}\n\n"
        else:
            example_message = ""
        prompt_message += example_message

        prompt_message += f"\n**Question:** {sample.question}\n**Answer:** SELECT"

        return prompt_message

    def _schema_info_prep(db_info, add_cv_ref: bool = False):
        # TODO:
        #   Add option to include only linked tables and columns
        #   Implement cv references
        message = ""
        tables = []
        for table in db_info:
            row = []
            for t_name, columns in table.items():
                for column in columns:
                    col_name = column["name"]
                    row.append(col_name)
                full_row = f"{t_name}: (" + ", ".join(row) + ")"
                tables.append(full_row)
        message += "\n".join(tables)
        message += "\n\n"

        return message

    def _fk_info_prep(db_info):
        message = ""
        for table in db_info:
            for t_name, columns in table.items():
                for column in columns:
                    if column["foreign"]:
                        message += f"{t_name}.{column['name']} references {column['foreign']}\n"
        return message + "\n"

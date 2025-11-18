import json
import re

class JsonFixer:
    # @staticmethod
    # def fix_and_parse_json(bad_json_string:str):
    #     # Escape unescaped control characters: \n, \r, \t
    #     def escape_control_chars(s):
    #         return re.sub(r'(?<!\\)([\n\r\t])', lambda m: '\\' + m.group(1), s)
    #
    #     cleaned = escape_control_chars(bad_json_string)
    #
    #     try:
    #         return json.loads(cleaned)
    #     except json.JSONDecodeError as e:
    #         print("JSON decode failed:", e)
    #         return None

    @staticmethod
    def fix_and_parse_json(bad_json_string):
        # print("Original input:\n", repr(bad_json_string))  # Debug line

        # Escape unescaped control characters
        def escape_control_chars(s):
            return re.sub(r'[\n\r\t]', '', s)
            # return re.sub(r'(?<!\\)([\n\r\t])', lambda m: '\\' + m.group(1), s)

        cleaned = escape_control_chars(bad_json_string)
        # print("\nCleaned JSON string:\n", cleaned)  # Debug line

        try:
            result = json.loads(cleaned)
            # print("\nParsed JSON:\n", result)  # Debug line
            return result
        except json.JSONDecodeError as e:
            print("JSON decode failed:", e)
            return None
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ipaddress
import json
import logging
import os
import re
import string
import time
from collections import Counter, defaultdict
from functools import lru_cache
from multiprocessing import Pool, cpu_count

import nh3
import numpy as np
import pandas as pd

from logsage.auto_resume_policy.consts import (
    BENIGN_WORDS,
    CONTEXT_SIZE,
    DOMAIN_SIZE,
    ERROR_WORDS,
    HARDWARE_WORDS,
    JOB_STARTED_NOT_DICT,
    LLM_ENDPOINT_FAILED,
    NOT_HARDWARE_WORDS,
)  # .

# Precompile regex patterns for better performance
NUMBER_PATTERN = re.compile(r"\d+")
ONLY_NUMBERS_PATTERN = re.compile(r"\b\d+\b")
QUOTED_TEXT_PATTERN = re.compile(r'(["\']).*?\1')
HEX_PATTERN = re.compile(r"\b0x[0-9a-fA-F]+\b")
LINUX_PATH_PATTERN = re.compile(r"(/(?:[\w.-]+/)*[\w.-]+)")


logger = logging.getLogger(__name__)


def retry_operation(operation, max_retries=5) -> str | list[str]:
    """Helper function to retry batch operations with fixed backoff.

    Args:
        operation: Callable that performs the batch operation
        max_retries: Maximum number of retry attempts

    Returns:
        Result of the operation if successful, empty list if all retries fail
    """
    attempt = 0
    while attempt < max_retries:
        try:
            result = operation()
            return result

        except Exception as e:
            attempt += 1
            logger.error(f"Attempt {attempt} failed: {e}. Retrying...")

            if attempt == max_retries:
                try:
                    list_llms = json.loads(os.environ["MODEL_LIST"])
                except (KeyError, json.JSONDecodeError) as parse_error:
                    logger.error(f"Failed to parse MODEL_LIST: {parse_error}")
                    list_llms = []

                from logsage.auto_resume_policy.log_sage import config

                if len(list_llms) > 1 and not config.PERSONAL_ENDPOINT:
                    model_name = handle_text_file(mode="read")
                    if model_name == "ExceptionFile":
                        try:
                            current_model = config.MODEL_NAME
                            if current_model and current_model in list_llms:
                                model_name = get_next_text(current_model, list_llms)
                            else:
                                model_name = list_llms[0]
                        except Exception as e:
                            logger.warning(f"Failed to get config.MODEL_NAME: {e}")
                            model_name = list_llms[0]

                    else:
                        model_name = get_next_text(model_name, list_llms)

                    handle_text_file(mode="write", content=model_name)

                logger.error(LLM_ENDPOINT_FAILED)
                return LLM_ENDPOINT_FAILED
            time.sleep(0.5)


def get_next_text(current_text, text_list):
    """Return the next text after `current_text` in `text_list`, circularly.
    If `current_text` is not found, return the first element.
    """
    if not text_list:
        raise ValueError("text_list cannot be empty.")

    try:
        idx = text_list.index(current_text)
        next_idx = (idx + 1) % len(text_list)
        return text_list[next_idx]
    except ValueError:
        # current_text not found → return the first element
        return text_list[0]


def convert_paths_to_token(text: str, path_token: str = "<PATH>") -> str:
    """Helper function to convert Linux paths in a log line to a token

    Args:
        text: log line
        path_token: token to replace Linux paths

    Returns:
        text after replacement
    """
    tokenized_text = LINUX_PATH_PATTERN.sub(path_token, text)
    return tokenized_text


def convert_numbers_to_token(text: str, token: str = "<NUMBER>") -> str:
    """Helper function convert number to token

    Args:
        text: log

    Returns:
        text after replacement
    """
    # Use precompiled regex for better performance
    tokenized_text = NUMBER_PATTERN.sub(token, text)
    return tokenized_text


def convert_only_numbers_to_token(text: str, token: str = "<NUMBER>") -> str:
    """Helper function convert number to token

    Args:
        text: log

    Returns:
        text after replacement
    """
    # Use precompiled regex for better performance
    tokenized_text = ONLY_NUMBERS_PATTERN.sub(token, text)
    return tokenized_text


def replace_quoted_text_with_token(input_text: str) -> str:
    """Helper function convert quote to token

    Args:
        input_text: log

    Returns:
        text after replacement
    """
    # Use precompiled regex for better performance
    modified_text = QUOTED_TEXT_PATTERN.sub("<TEXT>", input_text)
    return modified_text


def add_spaces_around_punctuation(text: str) -> str:
    """Adds spaces around punctuation marks in the text.

    Parameters:
    text (str): The input text to be modified.

    Returns:
    str: The text with spaces around punctuation marks.
    """
    # Use a pre-built translation table for punctuation
    translator = str.maketrans({p: f" {p} " for p in string.punctuation})
    text = text.translate(translator)
    # Remove extra spaces
    text = " ".join(text.split())
    return text


def convert_long_words_to_special_token(text: str, special_token: str = "<LONG>") -> str:
    """Converts words longer than 10 characters in the text to a special token.

    Parameters:
    text (str): The input text to be converted.
    special_token (str): The special token to replace long words with.

    Returns:
    str: The text with long words replaced by the special token.
    """
    # More efficient implementation with list comprehension
    return " ".join(special_token if len(token) > 14 else token for token in text.split())


def convert_hex_to_special_token(text: str, special_token="<HEX>") -> str:
    """Converts hexadecimal patterns in the text to a special token.

    Parameters:
    text (str): The input text to be modified.
    special_token (str): The special token to replace hexadecimal patterns with.

    Returns:
    str: The text with hexadecimal patterns replaced by the special token.
    """
    # Use precompiled regex for better performance
    modified_text = HEX_PATTERN.sub(special_token, text)
    return modified_text


def create_batches(
    text_list: list | None = None, text_pattern_list: list | None = None, max_batch_length: int = 500
) -> tuple[list[str], list[str]]:
    """Helper function to return batches of logs

    Args:
        text_list: log lines
        text_pattern_list: log patterns
        max_batch_length: batch size

    Returns:
        Batches of log lines
    """
    if text_list is None:
        text_list = []
    if text_pattern_list is None:
        text_pattern_list = []

    batches = []
    batches_pattern = []
    current_batch = ""
    current_batch_pattern = ""

    for i, text in enumerate(text_list):
        text = text[:max_batch_length]
        if len(current_batch) + len("\n") + len(text) <= max_batch_length:
            current_batch += "\n" + text
            current_batch_pattern += "\n" + text_pattern_list[i]
        else:
            batches.append(current_batch)
            batches_pattern.append(current_batch_pattern)
            current_batch = text
            current_batch_pattern = text_pattern_list[i]

    # Add the last batch
    if current_batch:
        batches.append(current_batch)
        batches_pattern.append(current_batch_pattern)

    return batches, batches_pattern


def create_batches_long(
    text_list: str, text_pattern_list: str, max_batch_length: int = 500
) -> tuple[list[str], list[str]]:
    """Helper function to return batches of logs

    Args:
        text_list: log lines
        text_pattern_list: log patterns
        max_batch_length: batch size

    Returns:
        Batches of log lines
    """
    batches = []
    batches_pattern = []
    batches_long = []
    current_batch = ""
    current_batch_pattern = ""
    current_batch_long = ""

    for i, text in enumerate(text_list):
        text_long = text
        text = text[:max_batch_length]
        if len(current_batch) + len("\n\n") + len(text) <= max_batch_length:
            current_batch += "\n\n" + text
            current_batch_pattern += "\n\n" + text_pattern_list[i]
            current_batch_long += "\n\n" + text_long
        else:
            batches.append(current_batch)
            batches_pattern.append(current_batch_pattern)
            batches_long.append(current_batch_long)
            current_batch = text
            current_batch_pattern = text_pattern_list[i]
            current_batch_long = text_long

    # Add the last batch
    if current_batch:
        batches.append(current_batch)
        batches_pattern.append(current_batch_pattern)
        batches_long.append(current_batch_long)

    return batches, batches_pattern, batches_long


def count_shared_words(list1: list | None = None, list2: list | None = None) -> int:
    """Helper function to count tokens between 2 list

    Args:
        list1: list1
        list2: list2

    Returns:
        Count of tokens
    """
    if list1 is None:
        list1 = []
    if list2 is None:
        list2 = []

    # Convert both lists to sets to remove duplicates and allow for set operations
    set1 = set(list1)
    set2 = set(list2)

    # Find the intersection of both sets
    shared_words = set1.intersection(set2)

    # Return the number of shared words
    return len(shared_words)


def extract_application_isolation(text: str) -> dict:
    """Helper function to extract info from LLM output

    Args:
        text: text

    Returns:
        dict of info
    """
    # Define regex patterns for extraction
    patterns = {
        "Nodes": r"Nodes:\s*(.+?),",
        "GPU ranks": r"GPU ranks:\s*(.*)",
        "Justification": r"Justification:\s*(.*)",
    }

    # Extract the relevant information using regex
    extracted_info = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            extracted_info[key] = match.group(1).strip()

    return extracted_info


def extract_software_attribution(text: str) -> dict:
    """Helper function to extract info from LLM output

    Args:
        text: text

    Returns:
        dict of info
    """
    # Define regex patterns for Explanation and Categorize
    patterns = {
        "Explanation": r"Explanation:\s*(.*)(?=2. Categorization:)",
        "Categorization": r"Categorization:\s*(.*)",
    }

    # Extract the relevant information using regex
    extracted_info = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extracted_info[key] = match.group(1).strip()

    return extracted_info


def extract_category_attribution(text: str) -> dict:
    """Helper function to extract info from LLM output

    Args:
        text: text

    Returns:
        dict of info
    """
    # Define regex patterns for Explanation and Categorize
    patterns = {"Categorization": r"Categorization:\s*(.*)"}

    # Extract the relevant information using regex
    extracted_info = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extracted_info[key] = match.group(1).strip()

    return extracted_info


def dict_to_long_text(dictionary: dict | None = None) -> str:
    """Helper function to convert dict to text

    Args:
        dictionary: dict

    Returns:
        text
    """
    if dictionary is None:
        dictionary = {}

    text = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            sub_text = f"{key.capitalize()}:\n"
            for sub_key, sub_value in value.items():
                sub_text += f" - {sub_key.capitalize()}: {sub_value}\n"
            text += sub_text
        elif isinstance(value, list):
            text += f"{key.capitalize()}: {', '.join(map(str, value))}.\n"
        else:
            text += f"{key.capitalize()}: {value}.\n"
    return text


def round_robin_ordering(data: list | None = None) -> list:
    """Helper function to convert dict to text

    Args:
        data: list

    Returns:
        list
    """
    if data is None:
        data = []

    node_dict = defaultdict(list)

    # Parse input and group texts by node
    for line in data:
        if ": " in line:
            node, text = line.split(": ", 1)
            node_dict[node].append(text)

    # Create round-robin order
    result = []
    while any(node_dict.values()):
        for node in list(node_dict.keys()):
            if node_dict[node]:
                result.append(f"{node}: {node_dict[node].pop(0)}")

    return result


def similar_with_duplicates(text1: str, text_list: list[str] | None = None) -> bool:
    """Helper function to check similarity between errors pattern, comparing how much text1 is similar to sentences in text_list

    Args:
        text1: str
        text_list: list[str]

    Returns:
        True if thr>0.4, False otherwise
    """
    if text_list is None:
        text_list = []

    text1 = re.sub(r"<.*?>", "", text1)
    text1 = re.sub(rf"[{re.escape(string.punctuation)}]", "", text1)
    text1 = re.sub(r"\s+", " ", text1).strip()
    words1 = clean_text(text1)

    counter1 = Counter(words1)
    total_words1 = sum(counter1.values())

    for text2 in text_list:
        text2 = re.sub(r"<.*?>", "", text2)
        text2 = re.sub(rf"[{re.escape(string.punctuation)}]", "", text2)
        text2 = re.sub(r"\s+", " ", text2).strip()
        words2 = clean_text(text2)
        counter2 = Counter(words2)

        # Count how many words (with duplicates) match
        match_count = sum(min(counter1[word], counter2[word]) for word in counter1)

        similarity = match_count / (total_words1 + 1e-6)
        if similarity >= 0.4:
            return True

    return False


def compress_application_log_without_num(
    errors_application_logs_full: list | None = None, compress_length: int = CONTEXT_SIZE // 2
) -> str:
    """Helper function to compress to list of errors to log with errors

    Args:
        errors_application_logs_full: List (log, pattern, i)
        compress_length: compress size

    Returns:
        application log
    """
    if errors_application_logs_full is None:
        errors_application_logs_full = []

    # Step 1: Collect nodes for each pattern
    pattern_to_nodes = defaultdict(set)

    for error, pattern, location in errors_application_logs_full:
        node = error.split(":")[0]  # Extract "node<number>"
        pattern_to_nodes[pattern].add(node)

    # Step 2: Filter out errors where the pattern appears in >3 unique nodes
    filtered_errors_first = [
        (error, pattern, location)
        for error, pattern, location in errors_application_logs_full
        if len(pattern_to_nodes[pattern]) <= 2
    ]

    not_filtered_errors = [
        (error, pattern, location)
        for error, pattern, location in errors_application_logs_full
        if len(pattern_to_nodes[pattern]) > 2
    ]

    not_filtered_errors_list = [error[1] for error in not_filtered_errors]

    filtered_errors = [
        (error, pattern, location)
        for error, pattern, location in filtered_errors_first
        if not similar_with_duplicates(pattern, not_filtered_errors_list)
    ]

    if len(filtered_errors) == 0:
        return ""

    global_amount_per_pattern = int(compress_length / len(pd.unique([error[1] for error in filtered_errors])))
    amount_per_pattern = {}
    for log in filtered_errors:
        amount_per_pattern[log[1]] = int(global_amount_per_pattern / len(log[0]))

    # Store pattern occurrences in reverse order
    pattern_logs = defaultdict(list)

    for log in sorted(filtered_errors, key=lambda x: x[2], reverse=True):  # Start from the last element
        text, pattern, location = log
        if len(pattern_logs[pattern]) < amount_per_pattern.get(pattern, 0):
            pattern_logs[pattern].append(log)

    # Flatten the result while preserving order from last to first per pattern
    result = [log for logs in pattern_logs.values() for log in logs]
    result = sorted(result, key=lambda x: x[2])
    result = [log[0] for log in result]
    return "\n".join(result)[-compress_length:]


def compress_application_log(
    errors_application_logs_full: list | None = None, compress_length: int = CONTEXT_SIZE // 2
) -> str:
    """Helper function to compress to list of errors to log with errors

    Args:
        errors_application_logs_full: List (log, pattern, i)
        compress_length: compress size

    Returns:
        application log
    """
    if errors_application_logs_full is None:
        errors_application_logs_full = []

    application_errors_list = [error[0] for error in errors_application_logs_full]
    application_log = "\n".join(application_errors_list)

    if len(application_log) > CONTEXT_SIZE // 2:
        result_dict = {}

        for s in errors_application_logs_full:
            # Unpack the set; assume each set contains exactly two elements
            x, y, t = s
            # Append x to the list of the corresponding key y in the dictionary
            if y in result_dict:
                result_dict[y].append(x)
            else:
                result_dict[y] = [x]
        num_min_per_type = int(compress_length / len(result_dict.keys()))
        batch_concise = [
            "\n".join(pd.unique(round_robin_ordering(result_dict[key])))[:num_min_per_type] for key in result_dict
        ]
        application_log = "\n".join(batch_concise)
    return application_log


def compress_application_log_ordered(
    errors_application_logs_full: list | None = None,
    traceback_dict: dict | None = None,
    compress_length: int = CONTEXT_SIZE // 2,
) -> str:
    """Helper function to compress to list of errors to log with errors by order

    Args:
        errors_application_logs_full: List (log, pattern, i)
        compress_length: compress size

    Returns:
        application log
    """
    if errors_application_logs_full is None:
        errors_application_logs_full = []
    if traceback_dict is None:
        traceback_dict = {}

    global_amount_per_pattern = int(
        compress_length / len(pd.unique([error[1] for error in errors_application_logs_full]))
    )
    amount_per_pattern = {}
    for log in errors_application_logs_full:
        amount_per_pattern[log[1]] = int(global_amount_per_pattern / len(log[0]))

    # Store pattern occurrences in reverse order
    pattern_logs = defaultdict(list)

    for log in sorted(errors_application_logs_full, key=lambda x: x[2], reverse=True):  # Start from the last element
        text, pattern, location = log
        if len(pattern_logs[pattern]) < amount_per_pattern.get(pattern, 0):
            pattern_logs[pattern].append(log)

    # Flatten the result while preserving order from last to first per pattern
    result = [log for logs in pattern_logs.values() for log in logs]
    result = sorted(result, key=lambda x: x[2])
    # Convert the list of tuples into a set for faster lookups
    log_set = set([(error[0], error[1]) for error in result])
    result_0 = [log[0] for log in result]
    result_log_0 = "\n".join(result_0)

    if len(result_log_0) < compress_length:
        # Remove logs from the dictionary if they exist in log_set
        for template, logs in traceback_dict.items():
            traceback_dict[template] = [log for log in logs if (log, template) not in log_set]

        log_full = []
        for log in result:
            if log[1] in traceback_dict:
                log_full.extend(traceback_dict[log[1]])
                log_full.append(log[0])
                del traceback_dict[log[1]]
            else:
                log_full.append(log[0])
        result_log_full = "\n".join(log_full)

        if len(result_log_full) < compress_length:
            result_log_0 = result_log_full

    return result_log_0[-compress_length:]


def check_errors_after_iterations(
    errors_application_logs_full: list | None = None, iteration_patterns: list | None = None
) -> dict:
    """Helper function to check errors after iterations

    Args:
        errors_application_logs_full: List (log, pattern, i)

    Returns:
        dict of errors after iterations
    """
    if errors_application_logs_full is None:
        errors_application_logs_full = []
    if iteration_patterns is None:
        iteration_patterns = []

    dict_positions = {}
    for i in range(len(errors_application_logs_full)):
        if check_if_iteration(
            errors_application_logs_full[i][0], errors_application_logs_full[i][1], iteration_patterns
        ):
            dict_positions["iteration"] = errors_application_logs_full[i][2]
        elif any(word in errors_application_logs_full[i][0].lower() for word in ERROR_WORDS):
            if errors_application_logs_full[i][1] not in dict_positions:
                dict_positions[errors_application_logs_full[i][1]] = errors_application_logs_full[i][2]
    if "iteration" in dict_positions:
        iteration_value = dict_positions["iteration"]
        return {k: v for k, v in dict_positions.items() if k != "iteration" and v >= iteration_value}
    return {}


def clean_text(text: str) -> list[str]:
    """Helper function to clean punctuation marks from text

    Args:
        text: str

    Returns:
        list of text after removing punctuation marks
    """
    # Lowercase and remove punctuation
    translator = str.maketrans("", "", string.punctuation)
    return text.translate(translator).lower().split()


def is_95_percent_similar_with_duplicates(text1: str, text_list: list[str] | None = None) -> bool:
    """Helper function to check similarity between errors, comparing how much text1 is similar to sentences in text_list

    Args:
        text1: str
        text_list: list[str]

    Returns:
        True if thr>14/15, False otherwise
    """
    if text_list is None:
        text_list = []

    words1 = clean_text(text1)
    if len(words1) < 15:
        return False  # Reject if less than 10 words

    counter1 = Counter(words1)
    total_words1 = sum(counter1.values())

    for text2 in text_list:
        words2 = clean_text(text2)
        counter2 = Counter(words2)

        # Count how many words (with duplicates) match
        match_count = sum(min(counter1[word], counter2[word]) for word in counter1)

        similarity = match_count / total_words1
        if similarity >= 14 / 15:
            return True

    return False


def get_templates_before_last_n_iterations(tuples, N, iteration_patterns):
    iteration_indices = [
        i for i, (line, template, _) in enumerate(tuples) if check_if_iteration(line, template, iteration_patterns)
    ]

    if len(iteration_indices) <= N:
        return []

    cutoff_index = iteration_indices[-N]

    return [template for i, (_, template, _) in enumerate(tuples) if i < cutoff_index]


def remove_pre_cutoff_templates(tuples, N, iteration_patterns):
    # Step 1: Get templates before cutoff
    templates_to_remove = set(get_templates_before_last_n_iterations(tuples, N, iteration_patterns))

    # Step 2: Filter out all tuples with these templates
    filtered_tuples = [(line, template, idx) for (line, template, idx) in tuples if template not in templates_to_remove]

    return filtered_tuples


def compress_application_log_ordered_cut(
    errors_application_logs_full: list | None = None,
    traceback_dict: dict | None = None,
    iteration_patterns: list | None = None,
    started: str = "",
    compress_length: int = CONTEXT_SIZE // 2,
) -> tuple[str, bool]:
    """Helper function to compress to list of errors to log with errors by order

    Args:
        errors_application_logs_full: List (log, pattern, i)
        compress_length: compress size

    Returns:
        application log
    """
    if errors_application_logs_full is None:
        errors_application_logs_full = []
    if iteration_patterns is None:
        iteration_patterns = []
    if traceback_dict is None:
        traceback_dict = {}

    line_to_pattern = {line: pattern for line, pattern, _ in errors_application_logs_full}

    max_iter_index = -1
    error_patterns_before_iter = []
    if started == "JOB STARTED":
        for error in errors_application_logs_full:
            if check_if_iteration(error[0], error[1], iteration_patterns):
                max_iter_index = error[2]
        for error in errors_application_logs_full:
            if error[2] < max_iter_index and not check_if_iteration(error[0], error[1], iteration_patterns):
                error_patterns_before_iter.append(error[1])
    error_patterns_before_iter = list(pd.unique(error_patterns_before_iter))

    flag_remove = False

    dict_error_pattern = dict(
        zip(
            [error[0] for error in errors_application_logs_full],
            [error[1] for error in errors_application_logs_full],
            strict=True,
        )
    )

    mean_len = np.mean([len(error[0]) for error in errors_application_logs_full])
    global_amount_per_pattern = int(
        compress_length / len(pd.unique([error[1] for error in errors_application_logs_full]))
    )
    amount_per_pattern = {}
    for log in errors_application_logs_full:
        amount_per_pattern[log[1]] = int(global_amount_per_pattern / len(log[0]))

    errors_list = [error[0] for error in errors_application_logs_full]

    # Store pattern occurrences in reverse order
    pattern_logs = defaultdict(list)

    for log in sorted(errors_application_logs_full, key=lambda x: x[2], reverse=True):  # Start from the last element
        text, pattern, location = log
        if len(pattern_logs[pattern]) < amount_per_pattern.get(pattern, 0):
            pattern_logs[pattern].append(log)

    # Flatten the result while preserving order from last to first per pattern
    result = [log for logs in pattern_logs.values() for log in logs]
    result = sorted(result, key=lambda x: x[2])
    # Convert the list of tuples into a set for faster lookups
    log_set = set([(error[0], error[1]) for error in result])
    result_0 = [log[0] for log in result]
    result_log_0 = "\n".join(result_0)

    if len(result_log_0) < compress_length:
        # Remove logs from the dictionary if they exist in log_set
        for template, logs in traceback_dict.items():
            traceback_dict[template] = [
                log
                for log in logs
                if (log, template) not in log_set and not check_if_iteration(log, template, iteration_patterns)
            ]

        log_full = []
        for log in result:
            if log[1] in traceback_dict:
                log_full.extend(traceback_dict[log[1]])
                log_full.append(log[0])
                del traceback_dict[log[1]]
            else:
                log_full.append(log[0])
        result_log_full = "\n".join(log_full)

        if len(result_log_full) < compress_length and started == "JOB STARTED":
            result_log_0 = result_log_full

        result_log_0_lines = result_log_0.split("\n")
        count_iter = 0
        beginning_i = len(result_log_0_lines)  # Start at the last index

        if started == "JOB STARTED":
            for i in range(len(result_log_0_lines) - 1, -1, -1):  # Iterate from end to start
                line = result_log_0_lines[i]
                if line in line_to_pattern and check_if_iteration(line, line_to_pattern[line], iteration_patterns):
                    count_iter += 1
                    if count_iter == 5:
                        beginning_i = i  # Store the index
                        break

            result_log_cut = "\n".join(result_log_0_lines[beginning_i:])  # Trim log from 5th last occurrence
            if count_iter == 5:
                result_log_0 = result_log_cut

            max_iter = -1
            min_not_iter = -1
            for i in range(len(result_log_0_lines)):  # Iterate from end to start
                line = result_log_0_lines[i]
                if line in line_to_pattern and check_if_iteration(line, line_to_pattern[line], iteration_patterns):
                    max_iter = i
                elif min_not_iter == -1 and result_log_0_lines[i] in errors_list:
                    min_not_iter = i
            if min_not_iter != -1 and max_iter != -1 and min_not_iter > max_iter:
                result_log_0 = "\n".join(result_log_0_lines[min_not_iter:])
                flag_remove = True

            dict_positions = check_errors_after_iterations(errors_application_logs_full, iteration_patterns)
            result_log_0_lines_clean = []
            result_log_0_lines_clean_after = []
            if len(dict_positions) > 0:
                for line in result_log_0_lines:
                    if line in dict_error_pattern and dict_error_pattern[line] in dict_positions:
                        result_log_0_lines_clean.append(line)
                for line in result_log_0_lines_clean:
                    if not is_95_percent_similar_with_duplicates(dict_error_pattern[line], error_patterns_before_iter):
                        result_log_0_lines_clean_after.append(line)
                if len(result_log_0_lines_clean_after) > 0:
                    result_log_0 = "\n".join(result_log_0_lines_clean_after)
                    result_log_0 = result_log_0[:compress_length]
                    flag_remove = True
    # remove NCCL watchdog lines
    if len(errors_application_logs_full) > 0 and (
        "ProcessGroupNCCL.cpp:" not in errors_application_logs_full[0][0]
        and "NCCL watchdog" not in errors_application_logs_full[0][0]
    ):
        result_log_0_wo_nccl_watchdog = []
        result_log_0_lines = result_log_0.split("\n")
        for line in result_log_0_lines:
            if len(line) == 0:
                continue
            if "ProcessGroupNCCL.cpp:" in line or "NCCL watchdog" in line:
                break
            result_log_0_wo_nccl_watchdog.append(line)
        if len(result_log_0_wo_nccl_watchdog) > 0:
            result_log_0 = "\n".join(result_log_0_wo_nccl_watchdog)

    return result_log_0[-compress_length:], flag_remove


def compress_application_log_not_ordered_cut(
    errors_application_logs_full: list | None = None,
    traceback_dict: dict | None = None,
    iteration_patterns: list | None = None,
    started: str = "",
    compress_length: int = CONTEXT_SIZE // 2,
) -> tuple[str, bool]:
    """Helper function to compress to list of errors to log with errors by order

    Args:
        errors_application_logs_full: List (log, pattern, i)
        compress_length: compress size

    Returns:
        application log
    """
    if errors_application_logs_full is None:
        errors_application_logs_full = []
    if iteration_patterns is None:
        iteration_patterns = []
    if traceback_dict is None:
        traceback_dict = {}

    if started == "JOB STARTED":
        errors_application_logs_full_cutoff = remove_pre_cutoff_templates(
            errors_application_logs_full, 5, iteration_patterns
        )
        errors_application_logs_full = errors_application_logs_full_cutoff.copy()
        if len(errors_application_logs_full_cutoff) == 0:
            return "", True

    flag_remove = False

    global_amount_per_pattern = int(
        compress_length / len(pd.unique([error[1] for error in errors_application_logs_full]))
    )
    amount_per_pattern = {}
    for log in errors_application_logs_full:
        amount_per_pattern[log[1]] = int(global_amount_per_pattern / len(log[0]))

    errors_list = [error[0] for error in errors_application_logs_full]

    # Store pattern occurrences in reverse order
    pattern_logs = defaultdict(list)

    for log in errors_application_logs_full:  # Start from the last element
        text, pattern, location = log
        if len(pattern_logs[pattern]) < amount_per_pattern.get(pattern, 0):
            pattern_logs[pattern].append(log)

    # Flatten the result while preserving order from last to first per pattern
    result = [log for logs in pattern_logs.values() for log in logs]
    # Convert the list of tuples into a set for faster lookups
    log_set = set([(error[0], error[1]) for error in result])
    result_0 = [log[0] for log in result]
    result_log_0 = "\n".join(result_0)

    if len(result_log_0) < compress_length:
        # Remove logs from the dictionary if they exist in log_set
        for template, logs in traceback_dict.items():
            traceback_dict[template] = [
                log
                for log in logs
                if (log, template) not in log_set and not check_if_iteration(log, template, iteration_patterns)
            ]

        log_full = []
        for log in result:
            if log[1] in traceback_dict:
                log_full.extend(traceback_dict[log[1]])
                log_full.append(log[0])
                del traceback_dict[log[1]]
            else:
                log_full.append(log[0])
        result_log_0 = "\n".join(log_full)

    return result_log_0[-compress_length:], flag_remove


def compress_application_log_ordered_user_rec(
    errors_application_logs_full: list | None = None,
    traceback_dict: dict | None = None,
    iteration_patterns: list | None = None,
    started: str = "",
    compress_length: int = CONTEXT_SIZE // 2,
) -> tuple[str, bool]:
    """Helper function to compress to list of errors to log with errors by order

    Args:
        errors_application_logs_full: List (log, pattern, i)
        compress_length: compress size

    Returns:
        application log
    """
    if errors_application_logs_full is None:
        errors_application_logs_full = []
    if iteration_patterns is None:
        iteration_patterns = []
    if traceback_dict is None:
        traceback_dict = {}

    line_to_pattern = {line: pattern for line, pattern, _ in errors_application_logs_full}

    flag_remove = False

    dict_error_pattern = dict(
        zip(
            [error[0] for error in errors_application_logs_full],
            [error[1] for error in errors_application_logs_full],
            strict=True,
        )
    )

    global_amount_per_pattern = int(
        compress_length / len(pd.unique([error[1] for error in errors_application_logs_full]))
    )
    amount_per_pattern = {}
    for log in errors_application_logs_full:
        amount_per_pattern[log[1]] = int(global_amount_per_pattern / len(log[0]))

    errors_list = [error[0] for error in errors_application_logs_full]

    # Store pattern occurrences in reverse order
    pattern_logs = defaultdict(list)

    for log in sorted(errors_application_logs_full, key=lambda x: x[2], reverse=True):  # Start from the last element
        text, pattern, location = log
        if len(pattern_logs[pattern]) < amount_per_pattern.get(pattern, 0):
            pattern_logs[pattern].append(log)

    # Flatten the result while preserving order from last to first per pattern
    result = [log for logs in pattern_logs.values() for log in logs]
    result = sorted(result, key=lambda x: x[2])
    # Convert the list of tuples into a set for faster lookups
    log_set = set([(error[0], error[1]) for error in result])
    result_0 = [log[0] for log in result]
    result_log_0 = "\n".join(result_0)

    if len(result_log_0) < compress_length:
        # Remove logs from the dictionary if they exist in log_set
        for template, logs in traceback_dict.items():
            traceback_dict[template] = [
                log
                for log in logs
                if (log, template) not in log_set and not check_if_iteration(log, template, iteration_patterns)
            ]

        log_full = []
        for log in result:
            if log[1] in traceback_dict:
                log_full.extend(traceback_dict[log[1]])
                log_full.append(log[0])
                del traceback_dict[log[1]]
            else:
                log_full.append(log[0])
        result_log_full = "\n".join(log_full)

        if len(result_log_full) < compress_length:
            result_log_0 = result_log_full

        result_log_0_lines = result_log_0.split("\n")
        count_iter = 0
        beginning_i = len(result_log_0_lines)  # Start at the last index

        if started == "JOB STARTED":
            for i in range(len(result_log_0_lines) - 1, -1, -1):  # Iterate from end to start
                line = result_log_0_lines[i]
                if line in line_to_pattern and check_if_iteration(line, line_to_pattern[line], iteration_patterns):
                    count_iter += 1
                    if count_iter == 5:
                        beginning_i = i  # Store the index
                        break

            result_log_cut = "\n".join(result_log_0_lines[beginning_i:])  # Trim log from 5th last occurrence
            if count_iter == 5:
                result_log_0 = result_log_cut

            max_iter = -1
            min_not_iter = -1
            for i in range(len(result_log_0_lines)):  # Iterate from end to start
                line = result_log_0_lines[i]
                if line in line_to_pattern and check_if_iteration(line, line_to_pattern[line], iteration_patterns):
                    max_iter = i
                elif min_not_iter == -1 and result_log_0_lines[i] in errors_list:
                    min_not_iter = i
            if min_not_iter != -1 and max_iter != -1 and min_not_iter > max_iter:
                result_log_0 = "\n".join(result_log_0_lines[min_not_iter:])
                flag_remove = True

            dict_positions = check_errors_after_iterations(errors_application_logs_full, iteration_patterns)
            result_log_0_lines_clean = []
            if len(dict_positions) > 0:
                for line in result_log_0_lines:
                    if line in dict_error_pattern and dict_error_pattern[line] in dict_positions:
                        result_log_0_lines_clean.append(line)
                if len(result_log_0_lines_clean) > 0:
                    result_log_0 = "\n".join(result_log_0_lines_clean)
                    result_log_0 = result_log_0[:compress_length]
                    flag_remove = True

    return result_log_0[-compress_length:], flag_remove


def check_if_iteration(
    text: str,
    pattern: str = "",
    iteration_patterns: list | None = None,
) -> bool:
    """Helper function to check if the line is iteration signatures

    Args:
        text: log line

    Returns:
        True or False
    """
    if iteration_patterns is None:
        iteration_patterns = []

    if pattern and iteration_patterns:
        if pattern in iteration_patterns:
            return True

    # Change to regex + lower before
    text_lower = text.lower()
    if (
        ("iter_speed" in text_lower and "seconds per iteration | loss" in text_lower)
        or (
            "training:" in text_lower
            and ("%" in text_lower)
            and "|" in text_lower
            and "/" in text_lower
            and "[" in text_lower
        )
        or ("epoch" in text_lower and "train_loss" in text_lower and "lr" in text_lower)
        or (
            "epoch" in text_lower
            and "loss_step" in text_lower
            and "train_loss" in text_lower
            and "loss_epoch" in text_lower
        )
        or (
            "iteration" in text_lower
            and "consumed samples" in text_lower
            and "elapsed time per iteration" in text_lower
        )
        or ("iteration" in text_lower and "hit counter" in text_lower and "loss" in text_lower and "time" in text_lower)
        or (
            "training steps" in text_lower
            and "train_grad_norm" in text_lower
            and "train_loss" in text_lower
            and "train_consumed_samples" in text_lower
        )
        or ("iteration" in text_lower and "|" in text_lower and "loss" in text_lower)
        or ("%|" in text_lower and "/" in text_lower and "â" in text_lower and "[" in text_lower)
        or ("loss" in text_lower and "learning_rate" in text_lower and "epoch" in text_lower)
        or (
            ("training steps:" in text_lower and "train_loss" in text_lower and "train_consumed_samples" in text_lower)
            or ("TFLOP/s/device".lower() in text_lower)
        )
    ):
        return True
    return False


def check_order(logtext: str, text1: str, text2: str) -> bool:
    index1 = logtext.find(text1)
    index2 = logtext.find(text2, index1 + len(text1))  # Search for text2 after text1

    return index1 != -1 and index2 != -1  # Both should be found in correct order


def check_finished(app_log_full: str) -> str:
    """Helper function to check if the line is finished signatures

    Args:
        text: log line

    Returns:
        True or False
    """
    if "[exiting program after" in app_log_full:
        return "yes - [exiting program after exists"
    if check_order(app_log_full, "[after training is done]", "validation loss at iteration"):
        return "yes - [after training is done]"
    if "`Trainer.fit` stopped: `max_epochs=" in app_log_full:
        return "yes - `Trainer.fit` stopped: `max_epochs=` reached"
    # if 'Done with training' in app_log_full:
    #    return 'yes - Done with training'
    if "yotta" in app_log_full and app_log_full.split("\n")[-1] == "Finished":
        return "yes - yotta Finished"
    return "no"


def check_checkpoint(text: str) -> bool:
    """Helper function to check if the line is checkpoint signatures

    Args:
        text: log line

    Returns:
        True or False
    """
    text_lower = text.lower()

    if (
        "zero checkpoint saved" in text_lower
        or "successfully saved checkpoint from iteration" in text_lower
        or "time spent on checkpoint saving" in text_lower
        or "saved checkpoint (" in text_lower
        or "saved checkpoint (remote)" in text_lower
    ):
        return True
    return False


def remove_not_errors(errors_list: list | None = None) -> list:
    """Helper function to remain logs that are errors

    Args:
        errors_list: log lines

    Returns:
        errors_list after filtering
    """
    if errors_list is None:
        errors_list = []

    words = BENIGN_WORDS

    errors_list = [errors_list[i] for i in range(len(errors_list)) if not any(word in errors_list[i] for word in words)]

    return errors_list


def return_not_benign(errors: list | None = None) -> bool:
    """Helper function to remove logs that are not errors

    Args:
        errors: log lines

    Returns:
        errors_list after filtering
    """
    if errors is None:
        errors = []

    words = BENIGN_WORDS

    return not any(word in errors for word in words)


def node_to_rank(s: str) -> str:
    """Helper function to convert node to rank

    Args:
        s: text

    Returns:
        s after convertion
    """
    match = re.fullmatch(r"node(\d+)", s)
    if match:
        number = int(match.group(1)) * DOMAIN_SIZE
        return "ranks" + str(number) + "-" + str(number + DOMAIN_SIZE - 1)
    return s


def get_regex_errors(errors_list: list | None = None) -> list:
    """Helper function to remain logs that are errors

    Args:
        errors_list: log lines

    Returns:
        errors_list after filtering
    """
    if errors_list is None:
        errors_list = []

    words = ERROR_WORDS

    errors_list_regex = [
        errors_list[i] for i in range(len(errors_list)) if any(word in errors_list[i].lower() for word in words)
    ]

    return errors_list_regex


def get_hardware_regex_errors(errors_list: list | None = None) -> list:
    """Helper function to remain logs that are hardware errors

    Args:
        errors_list: log lines

    Returns:
        errors_list after filtering
    """
    if errors_list is None:
        errors_list = []

    words = HARDWARE_WORDS

    errors_list_regex = [
        errors_list[i] for i in range(len(errors_list)) if any(word in errors_list[i] for word in words)
    ]

    return errors_list_regex


def get_not_hardware_regex_errors(errors_list: list | None = None) -> list:
    """Helper function to remain logs that are hardware errors

    Args:
        errors_list: log lines

    Returns:
        errors_list after filtering
    """
    if errors_list is None:
        errors_list = []

    words = NOT_HARDWARE_WORDS

    errors_list_regex = [
        errors_list[i] for i in range(len(errors_list)) if any(word in errors_list[i] for word in words)
    ]

    return errors_list_regex


@lru_cache(maxsize=1024)
def similarity_score(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings (cached for performance)"""
    # Existing implementation with caching decorator
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    # Calculate intersection and union
    intersection = words1.intersection(words2)
    union = words1.union(words2)

    # Calculate Jaccard similarity if union is not empty
    if union:
        return len(intersection) / len(union)
    return 0.0  # If both are empty, similarity is 0


# Improve existing find_similar_lines function
def find_similar_lines(line: str, lines: list | None = None, threshold: float = 0.8) -> tuple:
    """Find similar lines with optimized approach"""
    if lines is None:
        lines = []

    # Use generator expression instead of list comprehension for memory efficiency
    return (i for i, other_line in enumerate(lines) if similarity_score(line, other_line) > threshold)


def check_ip_type(value: str) -> bool:
    """Helper function to check if the text is ip pattern

    Args:
        value: log line

    Returns:
        True or False
    """
    try:
        ip_obj = ipaddress.ip_address(value)
        if isinstance(ip_obj, ipaddress.IPv4Address) or isinstance(ip_obj, ipaddress.IPv6Address):
            return True
    except ValueError:
        return False


def check_less_three(list_nodes: list | None = None) -> bool:
    """Helper function to check if the nodes are less than 3

    Args:
        list_nodes: log lines

    Returns:
        True or False
    """
    if list_nodes is None:
        list_nodes = []

    list_ips = [check_ip_type(node) for node in list_nodes]
    true_ips = sum(list_ips)
    if true_ips == 2 and len(list_nodes) == 4:
        return True
    return len(list_nodes) <= 3


def return_started_or_not_text(training_started: str) -> str:
    """Helper function to map between training started to text

    Args:
        training_started: started status

    Returns:
        started text
    """
    training_started_text = JOB_STARTED_NOT_DICT[training_started.lower()]
    return training_started_text


def get_templating(tm_text: list | None = None) -> list:
    """Helper function to create templating

    Args:
        tm_text: log lines

    Returns:
        patterns of log lines
    """
    if tm_text is None:
        tm_text = []

    tm_text_cleand = [convert_paths_to_token(text) for text in tm_text]
    tm_text_cleaned = [replace_quoted_text_with_token(text) for text in tm_text_cleand]
    tm_text_cleaned = [add_spaces_around_punctuation(text) for text in tm_text_cleaned]
    tm_text_cleaned = [convert_hex_to_special_token(text) for text in tm_text_cleaned]
    tm_text_cleaned = [convert_long_words_to_special_token(text) for text in tm_text_cleaned]
    tm_text_cleaned = [convert_numbers_to_token(text) for text in tm_text_cleaned]
    return tm_text_cleaned


def process_line_templating(line: str) -> str:
    """Apply all templating transformations to a single line"""
    line = convert_paths_to_token(line)
    line = replace_quoted_text_with_token(line)
    line = add_spaces_around_punctuation(line)
    line = convert_hex_to_special_token(line)
    line = convert_long_words_to_special_token(line)
    line = convert_numbers_to_token(line)
    return line


def get_templating_multiprocessing(tm_text: list | None = None) -> list:
    """Create templating patterns for a list of log lines using multiprocessing"""
    if tm_text is None:
        tm_text = []

    try:
        num_workers = min(cpu_count(), 8)  # Tune max workers
        with Pool(processes=num_workers) as pool:
            tm_text_cleaned = pool.map(process_line_templating, tm_text)
            return tm_text_cleaned
    except Exception as e:
        logger.warning(f"Multiprocessing failed, falling back to single-threaded: {e}")
        return get_templating(tm_text)


def sanitize_log_text(text: str) -> str:
    """Helper function to remove curly brackets

    Args:
        text: text

    Returns:
        text after replacement
    """
    return text.replace("{", "[").replace("}", "]")


def prepare_log_for_llm(log_text: str, max_length: int = CONTEXT_SIZE // 2) -> str:
    """Helper function to prepare log for llm

    Args:
        log_text: log_text
        max_length: max_length

    Returns:
        log for llm
    """
    text = sanitize_log_text(log_text)
    return text[-max_length:] if len(text) > max_length else text


def extract_attribution_explanation(text):
    """Extracts Attribution and Explanation from text.
    Works for both single-line and multi-line formats.

    Logic:
    1. Extract text after 'Attribution:' until a newline OR 'Explanation:'.
    2. Extract text after 'Explanation:' until the end of the text.
    """
    attribution_match = re.search(r"Attribution:\s*(.*?)(?:\n|Explanation:|$)", text, re.DOTALL | re.IGNORECASE)
    explanation_match = re.search(r"Explanation:\s*(.*)", text, re.DOTALL | re.IGNORECASE)

    attribution = attribution_match.group(1).strip().rstrip(",") if attribution_match else ""
    explanation = explanation_match.group(1).strip() if explanation_match else ""

    return {"attribution": text, "explanation": explanation}


def return_lines_size(index_to_add, original_lines):
    lines = [original_lines[i] for i in pd.unique(index_to_add)]
    return len("\n".join(lines))


def get_last_indices(data, pattern_lens):
    pattern_to_indices = defaultdict(list)
    for _, pattern, index in data:
        pattern_to_indices[pattern].append(index)

    indices = []
    for pattern, n_rows in pattern_lens.items():
        indices.extend(pattern_to_indices.get(pattern, [])[-n_rows:])
    return sorted(indices)


def expand_context(original_lines, tuples_list, max_len=CONTEXT_SIZE // 2):
    global_amount_per_pattern = int(max_len / max(1, len(pd.unique([error[1] for error in tuples_list]))))
    amount_per_pattern = {}
    for log in tuples_list:
        amount_per_pattern[log[1]] = int(global_amount_per_pattern / len(log[0]))

    errors_idx = get_last_indices(tuples_list, amount_per_pattern)  # [item[2] for item in tuples_list]
    index_to_add = get_last_indices(tuples_list, amount_per_pattern)  # [item[2] for item in tuples_list]

    # Check if the total length of lines in tuples already exceeds max_len
    initial_lines = [line for line, _, _ in tuples_list]
    if sum(len(line) for line in initial_lines) > max_len:
        return "\n".join([original_lines[i] for i in sorted(errors_idx)])

    offset_idx = 1
    while True:
        for i in errors_idx:
            if i - offset_idx > -1:
                index_to_add.append(i - offset_idx)
            if i + offset_idx < len(original_lines):
                index_to_add.append(i + offset_idx)
            if return_lines_size(index_to_add, original_lines) > max_len:
                return "\n".join([original_lines[i] for i in pd.unique(sorted(index_to_add))])
        offset_idx += 1
        if offset_idx >= 100:
            return "\n".join([original_lines[i] for i in pd.unique(sorted(index_to_add))])


def sanitize_xss(text: str):
    text = nh3.clean(text)
    return text


def extract_answer(text: str) -> str:
    """Remove the <think>...</think> reasoning part and return the remaining answer."""
    # Remove <think>...</think> (including newlines and any text inside)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Strip whitespace and return the remaining text
    return cleaned.strip()


def handle_text_file(mode="read", content=None, filename="model.txt"):
    """Read or write text to a file.

    Parameters:
    -----------
    mode : str
        "read" or "write"
    content : str or list
        Text or list of strings to write (ignored if mode="read")
    filename : str
        File path (default: "model.txt")
    append : bool
        If True and mode="write", appends instead of overwriting

    Returns:
    --------
    str or list[str] or None
        - Returns file content (as list of lines) if reading
        - None if writing
    """
    if mode == "write":
        if content is None:
            return "ExceptionFile"

        # Normalize list or string input
        if isinstance(content, list):
            content = "\n".join(map(str, content))

        file_mode = "w"
        with open(filename, file_mode, encoding="utf-8") as f:
            f.write(content.strip())

    elif mode == "read":
        if not os.path.exists(filename):
            # Return empty list instead of error
            return "ExceptionFile"

        with open(filename, encoding="utf-8") as f:
            return f.readline().strip()

    else:
        return "ExceptionFile"

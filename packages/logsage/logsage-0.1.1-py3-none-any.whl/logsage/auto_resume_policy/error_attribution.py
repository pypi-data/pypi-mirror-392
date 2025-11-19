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

import logging
import re

import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from logsage.auto_resume_policy.attribution_classes import ApplicationData  # .
from logsage.auto_resume_policy.consts import (
    BATCH_LLM_CALLS,
    CONTEXT_SIZE,
    DOMAIN_SIZE,
    HARDWARE_THR_CATEGORY,
    HARDWARE_THR_LINE,
    ISOLATION_COUNT,
    LLM_ENDPOINT_FAILED,
    POLICIES,  # .
)
from logsage.auto_resume_policy.prompts import (
    attribution_category_template,
    attribution_infra_template,
    cordon_node_global_1o1_template_num,
    cordon_node_global_template_num,
    suggest_no_checkpoint_restart,
    suggest_no_checkpoint_stop,
    suggest_yes_checkpoint_restart,
    suggest_yes_checkpoint_stop,
    template_app_error_cat,
    template_compute_networking_prompt,
    template_hardware_category_prompt,
    template_policy_instructions_output_format,
    template_policy_instructions_training_not_started,
    template_policy_instructions_training_started,
    template_policy_instructions_training_started_cut,
)
from logsage.auto_resume_policy.utils import (
    check_if_iteration,
    check_less_three,
    compress_application_log,
    compress_application_log_ordered,
    compress_application_log_ordered_cut,
    compress_application_log_ordered_user_rec,
    compress_application_log_without_num,
    extract_attribution_explanation,  # .
    get_hardware_regex_errors,
    get_not_hardware_regex_errors,
    node_to_rank,
    prepare_log_for_llm,
    retry_operation,
    return_started_or_not_text,
    sanitize_log_text,
)

# setup uvicorn logger
logger = logging.getLogger("uvicorn.error")

_rank_re = re.compile(r"^(\d+):")


def check_end_iteration(application_log, application_errors_list_iteration, iteration_patterns):
    application_log_lines = application_log.split("\n")
    # Check if all lines return True
    line_to_pattern = {line: pattern for line, pattern, _ in application_errors_list_iteration}
    list_items = [
        check_if_iteration(line, line_to_pattern[line], iteration_patterns)
        for line in application_log_lines
        if line in line_to_pattern
    ]
    all_iteration = all(list_items)
    return all_iteration and len(list_items) > 0


def parse_text_to_dict(text: str) -> dict:
    """Parses a formatted text into a dictionary.

    Args:
        text (str): The input text containing key-value pairs.

    Returns:
        dict: Parsed dictionary with categories as keys and their corresponding values.
    """
    pattern = r"'(.*?)':\s*(\d+)"  # Regex pattern to extract key-value pairs
    parsed_dict = {match[0]: int(match[1]) for match in re.findall(pattern, text)}
    return parsed_dict


def get_first_strings(tuples_list: list | None = None) -> tuple[list, list]:
    """Helper function returns error lines and patterns

    Args:
        tuples_list: List (log, pattern, i)

    Returns:
        2 lists: errors, patterns
    """
    if tuples_list is None:
        tuples_list = []

    unique_templates = {}

    for string, template, i in tuples_list:
        if template not in unique_templates:
            unique_templates[template] = string  # Store first occurrence

    return list(unique_templates.values()), list(unique_templates.keys())


def get_attribution_infra(llm, app_data):
    application_log_user_rec, flag_remove = compress_application_log_ordered_user_rec(
        app_data.application_errors_list_iteration,
        app_data.traceback_dict,
        app_data.iteration_patterns,
        app_data.training_started,
        CONTEXT_SIZE,
    )
    application_log_user_rec = sanitize_log_text(application_log_user_rec)

    template_proposed_solution = f"""{attribution_infra_template}
        These are the application errors: {application_log_user_rec}"""

    prompt_prop_sol = PromptTemplate.from_template(template_proposed_solution)

    prop_sol_chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
        | prompt_prop_sol
        | llm
        | StrOutputParser()
    )

    result_proposed_sol = retry_operation(lambda: prop_sol_chain.invoke(template_proposed_solution))

    if result_proposed_sol == LLM_ENDPOINT_FAILED:
        return {"attribution": "", "explanation": ""}

    attribution_dict = extract_attribution_explanation(result_proposed_sol)

    return attribution_dict


def get_proposed_solution_cat(
    llm: ChatNVIDIA,
    app_data: ApplicationData,
    isolation: bool = False,
    attribution: bool = True,
    verbose: bool = True,
) -> str:
    """Function return category of the errors

    Args:
        app_data: ApplicationData:
            application_errors_list_full: List (log, pattern, i)
            application_errors_list_iteration: List (log, pattern, i), with iteration signatures
            traceback_dict: Dict of stacktraces
            training_started: Training status

    Returns:
        job resume-policy and cordon ambiguous nodes
    """
    logger.info("Errors categorization started")

    # Create text for training started or not for LLM
    training_started_text = return_started_or_not_text(app_data.training_started)

    # Create application log based on errors
    application_log = compress_application_log(app_data.application_errors_list_full)
    application_log = prepare_log_for_llm(application_log, max_length=CONTEXT_SIZE // 2)

    template_hardware_category = (
        template_hardware_category_prompt
        + f"""
    These are the application errors: {application_log}

    Additional information: {training_started_text}, take it in consideration when suggesting category.

    """
    )

    prompt_sol = PromptTemplate.from_template(template_hardware_category)

    app_sol_chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()} | prompt_sol | llm | StrOutputParser()
    )

    # Categorize the errors based LLM
    result_sol = retry_operation(lambda: app_sol_chain.invoke(template_hardware_category))

    if result_sol == LLM_ENDPOINT_FAILED:
        result_dict = {}
    else:
        result_dict = parse_text_to_dict(result_sol)

    hardware_score = 0
    numerical_instability_score = 0

    if result_dict:
        hardware_score = result_dict.get("HARDWARE", 0)
        numerical_instability_score = result_dict.get("NUMERICAL INSTABILITY", 0)

    if (
        "HARDWARE" in result_dict
        and (
            hardware_score >= HARDWARE_THR_CATEGORY
            or (hardware_score + numerical_instability_score >= HARDWARE_THR_CATEGORY and hardware_score >= 20)
        )
    ) or result_sol == LLM_ENDPOINT_FAILED:
        # identify the faulty node
        uniques, patterns = get_first_strings(app_data.application_errors_list_full)
        # Find cordon nodes
        result_isolation = (
            get_cordon_nodes(llm, app_data, uniques, patterns, isolation, attribution, verbose),
            app_data.training_started,
        )
        attribution_output = ""
        if "TEMPORAL ISOLATION" in result_isolation[0]:
            if attribution:
                attribution_output = "Infrastructure"

        attribution_explanation = ""

        if isinstance(result_isolation[0], tuple):
            auto_resume_output = result_isolation[0][0]
            auto_resume_explanation = result_isolation[0][1]
            if attribution:
                attribution_output = result_isolation[0][2]
                attribution_explanation = result_isolation[0][3]
        else:
            auto_resume_output = result_isolation[0].split("\n")[0]
            auto_resume_explanation = result_isolation[0].split("\n")[1]
            if attribution:
                attribution_dict = get_attribution_infra(llm, app_data)
                attribution_output = attribution_dict["attribution"]
                attribution_explanation = attribution_dict["explanation"]

        if verbose:
            result_output = (
                auto_resume_output,
                auto_resume_explanation,
                attribution_output,
                attribution_explanation,
                result_isolation[1],
            )
        else:
            result_output = auto_resume_output, "", attribution_output, "", result_isolation[1]

    else:
        # Provide resume policy
        result_output = get_proposed_solution_policies(llm, POLICIES, app_data, attribution, verbose)

    logger.info("Errors categorization ended")
    return result_output


def check_restart_or_stop(log_text: str) -> str:
    """Helper function to extract if the recommendation is stop ir restart immediate

    Args:
        log_text: Text of log

    Returns:
        'RESTART IMMEDIATE' and 'STOP - DONT RESTART IMMEDIATE'
    """
    # Extract values using regex
    restart_match = re.search(r"'RESTART THE JOB IMMEDIATELY':\s*(\d+)", log_text)
    stop_match = re.search(r"'NOT RESTART THE JOB IMMEDIATELY':\s*(\d+)", log_text)

    # Get values (default to None if not found)
    restart_value = int(restart_match.group(1)) if restart_match else None
    stop_value = int(stop_match.group(1)) if stop_match else None

    if restart_value is not None and stop_value is not None:
        bigger = "RESTART IMMEDIATE" if restart_value > stop_value else "STOP - DONT RESTART IMMEDIATE"
        return bigger
    return "RESTART IMMEDIATE"


def get_proposed_solution_policies(
    llm: ChatNVIDIA,
    policies: list,
    app_data: ApplicationData,
    attribution: bool = True,
    verbose: bool = True,
) -> tuple[str, str, str]:
    """Function to recommend resume policy

    Args:
        policies: Policies
        training_started: Status training
        application_errors_list_iteration: List (log, pattern, i), with iteration signatures
        traceback_dict: Dict stacktraces

    Returns:
        'RESTART IMMEDIATE' and 'STOP - DONT RESTART IMMEDIATE'
    """
    logger.info("Policy suggestion started")

    # Create the log based errors, iterations and stacktraces to LLM context size
    application_log, flag_remove = compress_application_log_ordered_cut(
        app_data.application_errors_list_iteration,
        app_data.traceback_dict.copy(),
        app_data.iteration_patterns,
        app_data.training_started,
        CONTEXT_SIZE,
    )

    end_iteration = check_end_iteration(
        application_log, app_data.application_errors_list_iteration, app_data.iteration_patterns
    )

    if end_iteration:
        application_log = compress_application_log_ordered(
            app_data.application_errors_list_iteration,
            app_data.traceback_dict.copy(),
            CONTEXT_SIZE,
        )

    # if end_iteration:
    #    if verbose:
    #        return "RESTART IMMEDIATE", "The training continues after the errors", "", "", app_data.training_started
    #    return "RESTART IMMEDIATE", "", "", "", app_data.training_started
    application_log = sanitize_log_text(application_log)
    if len(application_log) == 0:
        if verbose:
            return "RESTART IMMEDIATE", "The training continues after the errors", "", "", app_data.training_started
        return "RESTART IMMEDIATE", "", "", "", app_data.training_started

    policies_dict = {}

    logger.info(f"Checkpointing status: {app_data.checkpoint_saved}")
    logger.info(f"Training status: {app_data.training_started}")

    # if not app_data.checkpoint_saved and app_data.training_started == "JOB NOT STARTED":
    if not app_data.checkpoint_saved:
        policies_dict["Suggest to NOT RESTART THE JOB IMMEDIATELY"] = suggest_no_checkpoint_stop
        policies_dict["Suggest to RESTART THE JOB IMMEDIATELY"] = suggest_no_checkpoint_restart
    else:
        policies_dict["Suggest to NOT RESTART THE JOB IMMEDIATELY"] = suggest_yes_checkpoint_stop
        # if app_data.checkpoint_saved:
        #    policies_dict["Suggest to NOT RESTART THE JOB IMMEDIATELY"] += "\n" + suggest_yes_checkpoint_stop_extension
        policies_dict["Suggest to RESTART THE JOB IMMEDIATELY"] = suggest_yes_checkpoint_restart

    # General instructions
    if app_data.checkpoint_saved:  # app_data.training_started == "JOB STARTED" or app_data.checkpoint_saved:
        if not flag_remove:
            template_policy_instructions = template_policy_instructions_training_started
        else:
            template_policy_instructions = template_policy_instructions_training_started_cut
    else:
        template_policy_instructions = template_policy_instructions_training_not_started

    template_policy_instructions += "\n".join(
        f"{policy}, in the following cases:\n{policies_dict[policy]}" for policy in policies
    )
    template_policy_instructions = (
        template_policy_instructions
        + template_policy_instructions_output_format
        + f"""
    These are the application errors: {application_log}
    """
    )

    prompt_sol = PromptTemplate.from_template(template_policy_instructions)

    app_sol_chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()} | prompt_sol | llm | StrOutputParser()
    )

    result_sol = retry_operation(lambda: app_sol_chain.invoke(template_policy_instructions))

    if result_sol == LLM_ENDPOINT_FAILED:
        return LLM_ENDPOINT_FAILED, "", LLM_ENDPOINT_FAILED, "", app_data.training_started

    restart_or_stop = check_restart_or_stop(result_sol)
    # Regex pattern to extract the first occurrence after "Justification:" until the next newline or the end of text
    pattern = r"Justification:\s*([^\n]+)"

    # Find the first match
    match = re.search(pattern, result_sol)

    justification = ""
    if match:
        justification = match.group(1)
    result_output = restart_or_stop + "\n"
    result_output += justification

    result_proposed_sol = ""

    if attribution:
        template_proposed_solution = f"""{attribution_category_template}
            These are the application errors: {application_log}"""

        prompt_prop_sol = PromptTemplate.from_template(template_proposed_solution)

        prop_sol_chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | prompt_prop_sol
            | llm
            | StrOutputParser()
        )

        result_proposed_sol = retry_operation(lambda: prop_sol_chain.invoke(template_proposed_solution))

        if result_proposed_sol == LLM_ENDPOINT_FAILED:
            return LLM_ENDPOINT_FAILED, "", LLM_ENDPOINT_FAILED, "", app_data.training_started

    logger.info("Policy suggestion ended")

    attribution_dict = extract_attribution_explanation(result_proposed_sol)
    if verbose:
        return (
            result_output.split("\n")[0],
            result_output.split("\n")[1],
            attribution_dict["attribution"],
            attribution_dict["explanation"],
            app_data.training_started,
        )
    return result_output.split("\n")[0], "", attribution_dict["attribution"], "", app_data.training_started


def replace_number_with_rank(text: str) -> str:
    """Helper function to replace rank to node number

    Args:
        text: Log line

    Returns:
        Log lines after node replacement
    """
    text = text.strip()
    match = re.match(r"^(\d+):", text)
    if match:
        number = int(match.group(1))
        new_prefix = f"node{number // DOMAIN_SIZE}:"
        text = re.sub(r"^\d+:", new_prefix, text, count=1)
    return text


def get_gpu_rank(text: str) -> int | str:
    match = _rank_re.match(text)
    return int(match.group(1)) if match else ""


def get_node(text: str) -> str:
    """Helper function to get nodes

    Args:
        text: Log line

    Returns:
        Extract rank from text
    """
    text = text.strip()
    match = re.match(r"^(\d+):", text)
    number = ""
    if match:
        number = match.group(1)
        number = int(number) // DOMAIN_SIZE
    return str(number)


def categorize_errors(llm: ChatNVIDIA, unique_application_errors: list | None = None) -> list:
    """Helper function to give score for each line of being the hardware error

    Args:
        unique_application_errors: unique application errors

    Returns:
        List of hardware issues
    """
    if unique_application_errors is None:
        unique_application_errors = []

    unique_application_errors_confidence = dict.fromkeys(unique_application_errors, 0)

    unique_application_errors_hw_regex = get_hardware_regex_errors(unique_application_errors)
    for error in unique_application_errors_hw_regex:
        unique_application_errors_confidence[error] = 100

    unique_application_errors_not_hw_regex = get_not_hardware_regex_errors(unique_application_errors)
    for error in unique_application_errors_not_hw_regex:
        unique_application_errors_confidence[error] = 0

    unique_application_errors_remain = [
        error
        for error in unique_application_errors
        if error not in unique_application_errors_hw_regex and error not in unique_application_errors_not_hw_regex
    ]

    prompt = ChatPromptTemplate.from_template(template_app_error_cat)

    application_llm_categorization = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    )

    unique_application_errors_remain = unique_application_errors_remain[-BATCH_LLM_CALLS:]

    batch_answer = retry_operation(lambda: application_llm_categorization.batch(unique_application_errors_remain))

    if batch_answer == LLM_ENDPOINT_FAILED:
        list(unique_application_errors_confidence.values())

    batch_conf = []
    for i, conf in enumerate(batch_answer):
        match = re.search(r"\d+", conf)

        if match:
            first_number = int(match.group())
            unique_application_errors_confidence[unique_application_errors_remain[i]] = first_number

        else:
            unique_application_errors_confidence[unique_application_errors_remain[i]] = 0

    return list(unique_application_errors_confidence.values())


def get_networking_compute(llm: ChatNVIDIA, log_text: str) -> str:
    """Helper function to use LLM to categorize if the issue is compute or networking

    Args:
        log_text: Log application errors

    Returns:
        networking or compute
    """
    template_compute_networking = (
        template_compute_networking_prompt
        + f"""
    These are log errors:
    "
    {log_text}
    "
    """
    )

    prompt_compute_networking = PromptTemplate.from_template(template_compute_networking)

    compute_networking_chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
        | prompt_compute_networking
        | llm
        | StrOutputParser()
    )

    result_compute_networking = retry_operation(lambda: compute_networking_chain.invoke(template_compute_networking))

    if result_compute_networking == LLM_ENDPOINT_FAILED:
        result_compute_networking = "networking"

    return result_compute_networking


def get_cordon_nodes(
    llm: ChatNVIDIA,
    app_data: ApplicationData,
    unique_application_errors: list | None = None,
    patterns_errors: list | None = None,
    isolation: bool = True,
    attribution: bool = True,
    verbose: bool = True,
) -> str:
    """Function to use LLM to detect ambiguous bad nodes

    Args:
        app_data: ApplicationData:
            application_errors_list_full: List (log, pattern, i)
            application_errors_list_iteration: List (log, pattern, i), with iteration signatures
            traceback_dict: Dict of stacktraces
            training_started: Training status
        unique_application_errors: unique application errors
        patterns_errors: errors patterns

    Returns:
        Ambiguous bad nodes
    """
    if unique_application_errors is None:
        unique_application_errors = []
    if patterns_errors is None:
        patterns_errors = []

    logger.info("Nodes cordoning started")

    application_errors_list_full = app_data.application_errors_list_full

    # Categorize the hardware application errors
    batch_conf = categorize_errors(llm, unique_application_errors)

    # Extract all the hardware errors >= HARDWARE_THR_LINE confidence
    conf_pattern = dict(zip(patterns_errors, batch_conf, strict=True))

    errors_list_hardware_patterns = [
        patterns_errors[i] for i in range(len(patterns_errors)) if batch_conf[i] >= HARDWARE_THR_LINE
    ]

    errors_list_hardware_raw = [
        unique_application_errors[i]
        for i in range(len(unique_application_errors))
        if batch_conf[i] >= HARDWARE_THR_LINE
    ]

    errors_list_hardware_list = [
        error[0] for error in application_errors_list_full if error[1] in errors_list_hardware_patterns
    ]

    hardware_gpu_ranks = list(
        pd.unique([get_gpu_rank(error) for error in errors_list_hardware_list if get_gpu_rank(error) != ""])
    )

    errors_list_hardware_full = [
        error
        for error in application_errors_list_full
        if (error[1] in errors_list_hardware_patterns)
        or (
            get_gpu_rank(error[0]) != ""
            and get_gpu_rank(error[0]) in hardware_gpu_ranks
            and conf_pattern.get(error[1], 0) > 0
        )
    ]

    errors_list_hardware_full_no_gpu = [
        error for error in application_errors_list_full if (error[1] in errors_list_hardware_patterns)
    ]

    # If there is a match between port down and completion errors, we are removing the completion errors to try identifying other errors, we will add the port down as ambiguous bad node
    errors_list_hardware_full = [
        (replace_number_with_rank(error[0]), error[1], error[2])
        for error in errors_list_hardware_full
        if get_gpu_rank(error[0])
    ]

    networking_compute_text = get_networking_compute(llm, sanitize_log_text("\n".join(errors_list_hardware_raw)))

    networking_compute = {}
    # Extract key-value pairs using regex
    for line in networking_compute_text.strip().split("\n"):
        match = re.match(r"(\w+):\s*(\d+)", line)
        if match:
            key, value = match.groups()
            networking_compute[key] = int(value)

    if len(errors_list_hardware_full) > 0 or len(errors_list_hardware_full_no_gpu) > 0:
        gpu_ranks_flag = True

        cordon_node_global_template = cordon_node_global_template_num

        cordon_node_global_1o1_template = cordon_node_global_1o1_template_num

        if len(errors_list_hardware_full) == 0:
            errors_list_hardware_full = errors_list_hardware_full_no_gpu

            gpu_ranks_flag = False

        cordon_node_global = cordon_node_global_template

        training_started_text = return_started_or_not_text(app_data.training_started)

        cordon_node_global += f"""

        Additional information: {training_started_text}, take it in consideration when suggesting to cordon or not. If the errors happened before the the job training running  - probably you don't have to cordon the nodes.

        """

        if len(errors_list_hardware_full) > 0:
            if gpu_ranks_flag:
                application_log_hardware = compress_application_log_without_num(errors_list_hardware_full)
            else:
                application_log_hardware = "\n".join([error[0] for error in errors_list_hardware_full])
                application_log_hardware = application_log_hardware[:CONTEXT_SIZE]

        if len(application_log_hardware) == 0:
            result_sol = get_proposed_solution_policies(llm, POLICIES, app_data, attribution, verbose)

            return result_sol

        application_log_hardware = "\n".join(pd.unique(application_log_hardware.split("\n")))
        application_log_hardware = sanitize_log_text(application_log_hardware)

        cordon_node_global_text = cordon_node_global
        template_application_isolation = (
            cordon_node_global_text
            + f"""

                                                    This is the errors: {application_log_hardware}

                                                    """
        )
        prompt_application_isolation = PromptTemplate.from_template(template_application_isolation)

        application_isolation_chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | prompt_application_isolation
            | llm
            | StrOutputParser()
        )
        # Return the nodes that are potential faulty nodes
        result_isolate = retry_operation(lambda: application_isolation_chain.invoke(template_application_isolation))

        if result_isolate == LLM_ENDPOINT_FAILED:
            return LLM_ENDPOINT_FAILED

        result_isolate_first = result_isolate

        def parse_confidence(text: str) -> int | None:
            """Helper function to parse confidence

            Args:
                text: log

            Returns:
                Confidence
            """
            # Define a regex pattern to find the confidence value
            pattern = r"Confidence:\s*(\d+)"

            # Search for the pattern in the given text
            match = re.search(pattern, text)

            if match:
                confidence = int(match.group(1))  # Extract the confidence as an integer
                confidence_extraction = confidence
            else:
                return None, None

            # Extract the content between "Nodes:" and "Confidence:"
            match = re.search(r"Nodes:\s*(.*?)\s*,\s*Confidence:", text)

            if match:
                nodes = [node.strip() for node in match.group(1).split(",")]
                nodes_extraction = nodes
            else:
                return None, None

            return nodes_extraction, confidence_extraction

        nodes_list, confidence = parse_confidence(result_isolate)
        if confidence is not None and nodes_list is not None:
            confidence = int(confidence)
            # If the confidence of hardware is less than 80 or the amount or nodes are above 3 - don't cordon the nodes
            if confidence < 80 or len(nodes_list) > ISOLATION_COUNT:
                # Propose auto-resume based LLM

                result_sol = get_proposed_solution_policies(llm, POLICIES, app_data, attribution, verbose)

                return result_sol
            # Otherwise - provide confidence for cordoning per node
            if len(errors_list_hardware_full) > 0:
                if isolation:
                    cordon_node_global = cordon_node_global_1o1_template

                    training_started_text = return_started_or_not_text(app_data.training_started)

                    cordon_node_global += f"""

                    Additional information: {training_started_text}, take it in consideration when suggesting to cordon or not. If the errors happened before the the job training running  - probably you don't have to cordon the nodes.

                    """
                    application_log_hardware = compress_application_log_without_num(errors_list_hardware_full)
                    application_log_hardware = "\n".join(pd.unique(application_log_hardware.split("\n")))
                    application_log_hardware = sanitize_log_text(application_log_hardware)

                    cordon_node_global_text = cordon_node_global
                    template_application_isolation = (
                        cordon_node_global_text
                        + f"""

                                                                This is the errors: {application_log_hardware}

                                                                """
                    )
                    prompt_application_isolation = PromptTemplate.from_template(template_application_isolation)

                    application_isolation_chain = (
                        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
                        | prompt_application_isolation
                        | llm
                        | StrOutputParser()
                    )

                    # Return the nodes that are potential faulty nodes
                    result_isolate = retry_operation(
                        lambda: application_isolation_chain.invoke(template_application_isolation)
                    )

                    if result_isolate == LLM_ENDPOINT_FAILED:
                        return LLM_ENDPOINT_FAILED

                if (
                    "networking" in networking_compute
                    and "compute" in networking_compute
                    and int(networking_compute["networking"]) > int(networking_compute["compute"])
                ):
                    result_sol = get_proposed_solution_policies(llm, POLICIES, app_data, attribution, verbose)
                    return result_sol

                if isolation:
                    pattern = r"Node: (\S+), Confidence: (\d+)"
                    cordon_nodes = {
                        match[0]: int(match[1]) for match in re.findall(pattern, result_isolate) if int(match[1]) >= 80
                    }
                    if len(cordon_nodes) == 0:
                        # Split only the first 3 fields, and treat the rest as justification
                        # Extract nodes
                        nodes_match = re.search(r"Nodes:\s*(.*?)\s*,\s*Confidence:", result_isolate_first)
                        nodes = [n.strip() for n in nodes_match.group(1).split(",")] if nodes_match else []

                        # Extract confidence
                        confidence_match = re.search(r"Confidence:\s*(\d+)", result_isolate_first)
                        confidence = int(confidence_match.group(1)) if confidence_match else None

                        # Extract justification
                        justification_match = re.search(r"Justification:\s*(.+)", result_isolate_first)
                        justification = justification_match.group(1).strip() if justification_match else ""

                        # Create both dictionaries
                        cordon_nodes = dict.fromkeys(nodes, confidence)
                        cordon_justification = dict.fromkeys(nodes, justification)
                    else:
                        pattern = r"Node:\s*(\S+),.*?Justification:\s*([^\n]+)"
                        matches = re.findall(pattern, result_isolate)
                        cordon_justification = {node: justification for node, justification in matches}

                    if 100 in cordon_nodes.values():
                        # Remove all keys with value <= 80
                        cordon_nodes = {k: v for k, v in cordon_nodes.items() if v > 80}
                    else:
                        cordon_nodes = {k: v for k, v in cordon_nodes.items() if v >= 80}
                    if check_less_three(cordon_nodes):
                        result_isolate = "TEMPORAL ISOLATION + RESTART\n"
                        for node in cordon_nodes:
                            if node in cordon_justification:
                                result_isolate += node_to_rank(node) + ", " + cordon_justification[node] + "\n"
                    else:
                        result_sol = get_proposed_solution_policies(llm, POLICIES, app_data, attribution, verbose)
                        return result_sol
                else:
                    attribution_output = ""
                    attribution_explanation = ""

                    if attribution:
                        attribution_dict = get_attribution_infra(llm, app_data)
                        attribution_output = attribution_dict["attribution"]
                        attribution_explanation = attribution_dict["explanation"]

                    return (
                        "RESTART IMMEDIATE",
                        "",
                        attribution_output,
                        attribution_explanation,
                        app_data.training_started,
                    )

                logger.info("Nodes cordoning ended")
                return result_isolate
        else:
            result_sol = get_proposed_solution_policies(llm, POLICIES, app_data, attribution, verbose)
            return result_sol
    else:
        result_sol = get_proposed_solution_policies(llm, POLICIES, app_data, attribution, verbose)
        return result_sol

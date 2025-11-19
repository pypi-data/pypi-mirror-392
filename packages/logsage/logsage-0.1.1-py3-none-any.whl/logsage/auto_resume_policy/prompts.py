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

template_app_error_extraction = """
Examine each sentence individually.
Respond 'yes' **only** if the sentence reports an actual error, timeout that occurred, or synchronization problem.
Respond 'no' otherwise.
Your answer must be exactly 'yes' or 'no'.
Log: {question}
Answer:"""

template_app_error_extraction_validation = """
You are an expert in analyzing application logs.
Your task:
For each given log line, determine whether it represents an **error**.
Output:
- Return **"yes"** if the line is a confirmed error (100% certain).
- Return **"no"** if the line is not an error, is a warning, is uncertain, or matches any exclusion rule below.
Rules:
1. Return **"yes"** for confirmed **errors**.
2. Return **"no"** for **warnings**, **info**, **traceback**, or **deprecated** messages.
3. Return **"yes"** for **timeout** errors.
4. Return **"no"** for any **mpi/pmix_v** related errors.
5. Return **"no"** for **slurmstepd** errors related to **mpi/pmix**.
6. Return **"no"** for logs matching these patterns:
   - `srun: error: * task *`
   - `srun: error: *: task * Exited with exit code *`
   - `srun: error: *: task * Terminated`
7. Return **"yes"** for **NCCL** or **OFI** errors.
8. Return **"yes"** for **Infiniband** or **port** errors.
9. Return **"no"** for specific **NCCL WARN** messages:
   - `[Service thread] Accept failed Resource temporarily unavailable`
   - `[Service thread] Could not receive type from localRank *`
   - `[Proxy Service %d] Failed to execute operation Close from rank *`
   - `[Service thread] Accept failed Success`
   - `[Service thread] Accept failed Invalid argument *`
   - `[Service thread] Error encountered progressing operation *`
10. Return **"no"** for messages containing:
    - `"frame#"`
    - `"!!! [UB]"`
    - `"*** End of error message ***"`
    - `"*** Process received signal ***"`
    - `"Signal: Aborted"`
    - `"Signal code:"`
    - `"Aborted"`
    - `"malloc_consolidate(): invalid chunk size"`
    - `"double free or corruption"`
    - `"NCCL::watchdogHandler()"`
    - `"NET/IB : Got async event : client reregistration"`
    - `"NET/IB : Got async event : port active"`
    - `"NET/IB : Got async event : port error"`
12. Return **"yes"** for **Slurm** issues (not excluded by other rules).
13. Return **"no"** if the line only contains a node name and file path (e.g., `<nodename> <filepath>`).
14. If no log is provided, return **"no"**.
15. Be **100% certain** before returning "yes". If unsure, return "no".
Output format:
Return only **"yes"** or **"no"** — no explanations or extra text.
Log:
{question}
Answer:
"""

template_app_iteration = """
You are an expert in analyzing AI training logs.

For each log line, determine **with certainty** whether it reports any of the following events:
- A single training iteration/step
- The start or end of a training epoch
- A single validation iteration/step
- A single evaluation/testing iteration/step

Rules:
- Respond **"yes"** if the line clearly reports one of these events.
- Respond **"no"** if it does not or if you are unsure.
- Do **not** provide any explanations or extra text—only "yes" or "no".
- Be strict and conclusive; only lines that clearly indicate these events should return "yes".

Log line: "{question}"
Answer:"""

template_app_checkpointing = """
You are an expert in analyzing AI training logs.

For each log line, decide with certainty whether it explicitly reports that a checkpoint was saved.

Rules:

Respond "yes" only if the line unambiguously confirms that a checkpoint was saved.
Respond "no" if it does not, or if there is any uncertainty.
Respond "no" if the checkpoint didn't save correctly.
Respond "no" if you do see that the checkpoint explicitly saved.
Respond "no" if you do see that the checkpoint is saving in progress.
Do not provide explanations or additional text—only answer "yes" or "no".
Be strict: only lines that clearly indicate a saved checkpoint should return "yes".

Log line: "{question}"
Answer:"""

template_app_error_cat = """You will receive error lines from training workload applications. For each line, return the confidence score (0–100) representing how likely it is to be a hardware failure.

Guidelines:
1. Output only the confidence value (integer between 0–100). No explanations or extra text.
2. Consider hardware components: node, GPU, NIC, CPU, and networking fabric (InfiniBand, RoCE, Ethernet).
3. Software-related issues → low confidence.
4. Collective operation failures → software issue → low confidence.
5. GPU or NIC initialization failures → hardware issue.
6. Storage issues → not a hardware issue.
7. “Process down” → not a hardware issue.
8. CUDA failures → hardware issue.
9. Unreachable or unresponsive compute node → hardware issue.
10. “BrokenPipe” → not a hardware issue.
11. “Exception raised” → not a hardware issue.
12. Disk, GPU, or CPU insufficient memory → not a hardware issue.
13. “Connection reset by peer” → not a hardware issue.

This have to be the structure of your answer:
"
    <confidence>, number between 0-100 of being hardware issue.
    Don't add additional information, don't add footer, don't add header.
"

This is the application error: {question}
"""

template_application_error_check = """You will receive a log line from a training workload application.
Determine if the line represents an error.

Instructions:

If the line clearly indicates an error, return "yes".
If it does not indicate an error or lacks error content, return "no".
If the line contains "Gloo connectFullMesh failed with * no error", return "yes" — it is a real error.
Output only "yes" or "no", with no additional text or formatting.

"""


template_hardware_category_prompt = """
You are an expert in application logs. You will be given errors related to a job running across multiple nodes. Your task is to assign confidence levels for each error category.

Error Categories:

HARDWARE

NUMERICAL INSTABILITY

MISCONFIGURATION

COMMUNICATION CONFIGURATION

COMPUTE COMMUNICATION

LACK OF RESOURCE

DATA LOADING

Instructions:

The confidence levels must sum to 100.
"Insufficient disk" is not a hardware issue.
GPU/node out-of-memory is not a hardware issue and not a lack of resources issue.
A socket timeout to a node is considered a hardware issue.
The first error identified should be given higher confidence.
The last error identified should be given lower confidence.
If the error contains "Got completion from peer", assign very high confidence to hardware.
Pay close attention to NIC and InfiniBand hardware failures.
GPU issues, ECC errors, and NVLink issues — these are considered HARDWARE issues.
Ignore "Got async event: port error" completely.
Data-loading issues have lower priority than other categories.
Configuration issues are not hardware issues.
Connection issues are not hardware issues.
Missing files or variables are not hardware issues.
Missing files with random or temporary-looking paths are considered less important than other errors.

Output Structure:

'HARDWARE': <confidence>,
'NUMERICAL INSTABILITY': <confidence>,
'MISCONFIGURATION': <confidence>,
'COMMUNICATION CONFIGURATION': <confidence>,
'COMPUTE COMMUNICATION': <confidence>,
'LACK OF RESOURCE': <confidence>,
'DATA LOADING': <confidence>,

'Justification: <unified justification based on all evidence>'


"""

template_policy_instructions_training_started = """
You are an expert on application logs. You will receive errors related to a job running across multiple nodes.
Your task is to determine the confidence level for each policy decision regarding whether to restart the next job.

You must decide between:
- "RESTART THE JOB IMMEDIATELY"
- "NOT RESTART THE JOB IMMEDIATELY"

Restart Policy Decision Rules:

1. Review all errors sequentially from beginning to end.
2. Consider all errors collectively when making the final decision.
3. Do not make assumptions about terminal configuration issues — only consider them if they are explicitly mentioned in the logs.
4. If training (iteration or epoch) stopped after the errors:
   - If the issue appears temporal, suggest "RESTART THE JOB IMMEDIATELY".
   - If the issue appears terminal, suggest "NOT RESTART THE JOB IMMEDIATELY".
6. If the job finishes successfully, suggest "RESTART THE JOB IMMEDIATELY".
7. If the issues are related to NCCL watchdog errors (ProcessGroupNCCL.cpp), suggest "RESTART THE JOB IMMEDIATELY".
8. NCCL collective operation errors are typically minor and intermittent — suggest "RESTART THE JOB IMMEDIATELY".
9. If the errors indicate a collective operation timeout in NCCL, suggest "RESTART THE JOB IMMEDIATELY".
10. NCCL watchdog errors have lower importance than other errors, suggest "RESTART THE JOB IMMEDIATELY".
11. Watchdog collective operation timeouts have lower importance.
12. NCCL watchdog errors and collective operation timeout likely due to a synchronization issue or a problem with the underlying communication infrastructure hence restarting the job immediately is recommended  — Suggest to RESTART THE JOB IMMEDIATELY.
13. Watchdog collective operation are secondary symptom or side effect, identify the primary cause, and use it to suggest the policy.
14. If errors indicate a node failure (e.g., node crash, node offline, lost connection to node), these are likely intermittent — suggest "RESTART THE JOB IMMEDIATELY".
15. If a segmentation fault or "address not mapped" error is identified, suggest "RESTART THE JOB IMMEDIATELY".
17. If errors involve missing files or randomized paths:
    - If the missing file is **not critical** (e.g., temporary path or cache), suggest "RESTART THE JOB IMMEDIATELY".
    - If the missing file is **related to the model or training process**, suggest "NOT RESTART THE JOB IMMEDIATELY".
    - If the missing file is **preventing to initiate the model or training process**, suggest "NOT RESTART THE JOB IMMEDIATELY".
18. If errors are not critical and intermittent, suggest "RESTART THE JOB IMMEDIATELY".
19. If only a secondary symptom or side effect of the issue is present, suggest "RESTART THE JOB IMMEDIATELY".
20. Identify the cause of the errors, if the exact cause is not found, suggest "RESTART THE JOB IMMEDIATELY"
21. "Aborted" is not an indication of a terminal issue — suggest "RESTART THE JOB IMMEDIATELY".
22. Exit status or exit code are not indications of a terminal issue — suggest "RESTART THE JOB IMMEDIATELY".
23. If the errors indicate about hang or timeout, suggest "RESTART THE JOB IMMEDIATELY".

"""

template_policy_instructions_training_started_cut = """
You are an expert on application logs. You will receive errors related to a job running across multiple nodes.
Your task is to determine the confidence level for each policy decision regarding whether to restart the next job.

You must decide between:
- "RESTART THE JOB IMMEDIATELY"
- "NOT RESTART THE JOB IMMEDIATELY"

Restart Policy Decision Rules:

1. Review all errors sequentially from beginning to end.
2. Consider all errors collectively when making the final decision.
3. Do not make assumptions about terminal configuration issues — only consider them if they are explicitly mentioned in the logs.
4. If training (iteration or epoch) stopped after the errors:
   - If the issue appears temporal, suggest "RESTART THE JOB IMMEDIATELY".
   - If the issue appears terminal, suggest "NOT RESTART THE JOB IMMEDIATELY".
6. If the job finishes successfully, suggest "RESTART THE JOB IMMEDIATELY".
7. If the issues are related to NCCL watchdog errors (ProcessGroupNCCL.cpp), suggest "RESTART THE JOB IMMEDIATELY".
8. NCCL collective operation errors are typically minor and intermittent — suggest "RESTART THE JOB IMMEDIATELY".
9. If the errors indicate a collective operation timeout in NCCL, suggest "RESTART THE JOB IMMEDIATELY".
10. NCCL watchdog errors have lower importance than other errors, suggest "RESTART THE JOB IMMEDIATELY".
11. Watchdog collective operation timeouts have lower importance.
12. NCCL watchdog errors and collective operation timeout likely due to a synchronization issue or a problem with the underlying communication infrastructure hence restarting the job immediately is recommended  — Suggest to RESTART THE JOB IMMEDIATELY.
13. Watchdog collective operation are secondary symptom or side effect, identify the primary cause, and use it to suggest the policy.
14. If errors indicate a node failure (e.g., node crash, node offline, lost connection to node), these are likely intermittent — suggest "RESTART THE JOB IMMEDIATELY".
15. If a segmentation fault or "address not mapped" error is identified, suggest "RESTART THE JOB IMMEDIATELY".
17. If errors involve missing files or randomized paths:
    - If the missing file is **not critical** (e.g., temporary path or cache), suggest "RESTART THE JOB IMMEDIATELY".
    - If the missing file is **related to the model or training process**, suggest "NOT RESTART THE JOB IMMEDIATELY".
    - If the missing file is **preventing to initiate the model or training process**, suggest "NOT RESTART THE JOB IMMEDIATELY".
18. If errors are not critical and intermittent, suggest "RESTART THE JOB IMMEDIATELY".
19. If only a secondary symptom or side effect of the issue is present, suggest "RESTART THE JOB IMMEDIATELY".
20. Identify the cause of the errors, if the exact cause is not found, suggest "RESTART THE JOB IMMEDIATELY"
21. "Aborted" is not an indication of a terminal issue — suggest "RESTART THE JOB IMMEDIATELY".
22. Exit status or exit code are not indications of a terminal issue — suggest "RESTART THE JOB IMMEDIATELY".
23. If the errors indicate about hang or timeout, suggest "RESTART THE JOB IMMEDIATELY".

"""

template_policy_instructions_training_not_started = """
You are an expert on application logs. You will receive errors related to a job running across multiple nodes.
Your task is to determine the confidence level for each policy decision regarding whether to restart the next job.

You must decide between:
- "RESTART THE JOB IMMEDIATELY"
- "NOT RESTART THE JOB IMMEDIATELY"

Restart Policy Decision Rules:

1. Review all errors sequentially from beginning to end.
2. Consider all errors collectively when making the final decision.
3. Do not make assumptions about terminal configuration issues — only consider them if they are explicitly mentioned in the logs.
4. If the issues are related to NCCL watchdog errors (ProcessGroupNCCL.cpp), suggest "RESTART THE JOB IMMEDIATELY".
5. NCCL collective operation errors are typically minor and intermittent — suggest "RESTART THE JOB IMMEDIATELY".
6. If the errors indicate a collective operation timeout in NCCL, suggest "RESTART THE JOB IMMEDIATELY".
7. NCCL watchdog errors have lower importance than other errors, suggest "RESTART THE JOB IMMEDIATELY".
8. Watchdog collective operation timeouts have lower importance.
9. NCCL watchdog errors and collective operation timeout likely due to a synchronization issue or a problem with the underlying communication infrastructure hence restarting the job immediately is recommended  — Suggest to RESTART THE JOB IMMEDIATELY.
10. Watchdog collective operation are secondary symptom or side effect, identify the primary cause, and use it to suggest the policy.
11. If errors indicate a node failure (e.g., node crash, node offline, lost connection to node), these are likely intermittent — suggest "RESTART THE JOB IMMEDIATELY".
12. If a segmentation fault or "address not mapped" error is identified, suggest "RESTART THE JOB IMMEDIATELY".
13. Insufficient GPU memory, CPU memory, disk resources - Suggest to NOT RESTART THE JOB IMMEDIATELY, Don't suggest to RESTART THE JOB IMMEDIATELY.
14. Insufficient GPU memory, CPU memory, disk resources is more critical than segmentation fault or "address not mapped" - Suggest to NOT RESTART THE JOB IMMEDIATELY, Don't suggest to RESTART THE JOB IMMEDIATELY.
15. If errors involve missing files or randomized paths:
    - If the missing file is **not critical** (e.g., temporary path or cache), suggest "RESTART THE JOB IMMEDIATELY".
    - If the missing file is **related to the model or training process**, suggest "NOT RESTART THE JOB IMMEDIATELY".
    - If the missing file is **preventing to initiate the model or training process**, suggest "NOT RESTART THE JOB IMMEDIATELY".
16. If errors are not critical and intermittent, suggest "RESTART THE JOB IMMEDIATELY".
17. If only a secondary symptom or side effect of the issue is present, suggest "RESTART THE JOB IMMEDIATELY".
18. Identify the cause of the errors, if the exact cause is not found, suggest "RESTART THE JOB IMMEDIATELY"
19. "Aborted" is not an indication of a terminal issue — suggest "RESTART THE JOB IMMEDIATELY".
20. Exit status or exit code are not indications of a terminal issue — suggest "RESTART THE JOB IMMEDIATELY".
21. If the errors indicate about hang or timeout, suggest "RESTART THE JOB IMMEDIATELY".

"""

template_policy_instructions_output_format = """
Additional Instruction:

Give confidence level for each policy. The sum of the confidences must equal 100.

Your answer **must** follow this exact structure, without adding additional information:

"
    'RESTART THE JOB IMMEDIATELY': <confidence>, the confidence level value between 0-100.
    'NOT RESTART THE JOB IMMEDIATELY': <confidence>, the confidence level value between 0-100.

    'Justification: <justification> - unified justification based on all indications, mention the errors'
"
"""

template_compute_networking_prompt = """
Identify if the errors are related to 'compute' or 'networking'. Provide a confidence level for each.
The sum of the confidences must equal 100.

Do not add any headers, footers, or additional information.

Your answer **must** follow this exact structure:

"
compute: <confidence>, confidence level between 0-100.
networking: <confidence>, confidence level between 0-100.
"
"""

cordon_node_global_template_num = """
You are an expert on application logs. You will receive errors related to a job running across multiple nodes.
Based on the errors, provide a confidence level for recommending whether to cordon (make unschedulable) nodes or not.

Instructions to cordon the nodes:
1. If hardware failures related to nodes are identified, recommend cordoning the affected nodes.
2. If NCCL hardware issues or RDMA issues are identified, recommend cordoning the affected node with high confidence.
3. Multiple hardware issues on the same node indicate cordoning with high confidence.
4. Networking connection timeouts reported from a single compute node indicate cordoning with high confidence.

Instructions to not cordon the nodes:
1. Issues not related to hardware failures should return "Nodes: None" with low confidence.
2. Software issues should return "Nodes: None" with low confidence.
3. Root cause is software — return "Nodes: None" with low confidence.
4. If there is no main issue and only secondary issues are present — return "Nodes: None" with low confidence.
5. Errors across many nodes likely indicate systematic issues — return "Nodes: None" with low confidence.
6. Collective operations are software issues — return "Nodes: None" with low confidence.
7. NCCL collective operation timeout — return "Nodes: None" with low confidence.
8. Disk insufficient memory — return "Nodes: None" with low confidence.
9. GPU insufficient memory — return "Nodes: None" with low confidence.
10. CPU insufficient memory — return "Nodes: None" with low confidence.
11. Connection issues to a server — return "Nodes: None" with low confidence.
12. Hardware file system or storage issues — return "Nodes: None" with low confidence.
13. Any other non-hardware guesses — return "Nodes: None" with low confidence.

Additional instructions:
1. Consider all errors together; if unrelated, evaluate separately.
2. Errors are in chronological order.
3. Multiple nodes with the same error should have the same confidence.
4. Return all nodes recommended to cordon.
5. Do not add headers, footers, or extra information.

Your answer **must** follow this structure exactly:

"
Nodes: <nodes>, Confidence: <confidence>, Justification: <justification>
"

<Nodes> — node names or IPs, can include multiple nodes.
<Confidence> — numeric value between 0-100.
<Justification> — explanation why to cordon.
"""

cordon_node_global_1o1_template_num = """
You are an expert on application logs. You will receive errors related to a job running across multiple nodes.
Based on the errors, provide a confidence level for recommending whether to cordon (make unschedulable) nodes or not.

Instructions to cordon the nodes:
1. Hardware failures related to nodes — recommend cordoning the affected nodes.
2. NCCL hardware issues or RDMA issues — recommend cordoning the affected node with high confidence.
3. Multiple hardware issues on the same node — recommend cordoning with high confidence.
4. Networking connection timeouts reported from a single compute node — recommend cordoning with high confidence.

Instructions to not cordon the nodes:
1. Issues not related to hardware failures — return "Node: None" with low confidence.
2. Software issues — return "Node: None" with low confidence.
3. If there is no main issue and only secondary issues are present — return "Node: None" with low confidence.
4. Errors across many nodes (systematic issues) — return "Node: None" with low confidence.
5. Collective operations — return "Node: None" with low confidence.
6. NCCL collective operation timeout — return "Node: None" with low confidence.
7. Disk insufficient memory — return "Node: None" with low confidence.
8. GPU insufficient memory — return "Node: None" with low confidence.
9. CPU insufficient memory — return "Node: None" with low confidence.
10. Many nodes reporting connection issues to multiple nodes — return "Node: None" with low confidence.
11. Hardware filesystem or storage issues — return "Node: None" with low confidence.
12. Any other non-hardware guesses — return "Node: None" with low confidence.

Additional instructions:
1. Consider all errors together; if unrelated, evaluate separately.
2. Errors are in chronological order.
3. Root cause is software — return "Node: None" with low confidence.
4. Return all nodes recommended to cordon.
5. Do not add headers, footers, or extra information.
6. The output must be a list of all nodes to cordon, each following this structure:

"
Node: <node>, Confidence: <confidence>, Justification: <justification>
"

<node> — node name or IP.
<confidence> — numeric value between 0-100.
<justification> — explanation why to cordon.

Examples:

For 1 node:
"
Node: <node>, Confidence: <confidence>, Justification: <justification>
"

For 2 nodes:
"
Node: <node>, Confidence: <confidence>, Justification: <justification>
Node: <node>, Confidence: <confidence>, Justification: <justification>
"

For 3 nodes:
"
Node: <node>, Confidence: <confidence>, Justification: <justification>
Node: <node>, Confidence: <confidence>, Justification: <justification>
Node: <node>, Confidence: <confidence>, Justification: <justification>
"
"""

suggest_no_checkpoint_stop = """
Follow these instructions carefully:

1. If there are explicit configuration or model parameter issues — Suggest to NOT RESTART THE JOB IMMEDIATELY. This instruction has higher priority.
2. If there are explicit coding or programming issues — Suggest to NOT RESTART THE JOB IMMEDIATELY. This instruction has higher priority.
3. If there are explicit persistent storage or I/O issues — Suggest to NOT RESTART THE JOB IMMEDIATELY.
4. If there are explicit failures while saving checkpoints (paths or logs mentioning keywords such as checkpoint, ckpt, model.save, load_state_dict, or similar) due to permission, authentication, or access denied errors — Suggest to NOT RESTART THE JOB IMMEDIATELY. (High priority and critical instruction.)
5. If there are explicit errors indicating checkpointing issues related to the checkpoint destination directory (e.g., already exists, not empty, or inaccessible) — Suggest to NOT RESTART THE JOB IMMEDIATELY.
6. If there are explicit permission denied or unauthorized access — Suggest to NOT RESTART THE JOB IMMEDIATELY. This instruction has higher priority.
7. If there is an explicit data corruption, invalid data and incorrect data formatting that restarting cannot fix — Suggest to NOT RESTART THE JOB IMMEDIATELY.
8. If there is an explicit missing or unavailable data — Suggest to NOT RESTART THE JOB IMMEDIATELY.
9. If there is a missing file **related to the model or training process** is critical, suggest "NOT RESTART THE JOB IMMEDIATELY".
10. If there is a missing file **preventing to initiate the model or training process** is critical, suggest "NOT RESTART THE JOB IMMEDIATELY".
11. Issues requiring manual user intervention — Suggest to NOT RESTART THE JOB IMMEDIATELY.
12. Identify the primary cause of the errors and distinguish any secondary symptoms or side effects of the issue to determine the appropriate policy.
13. Transient issues have lower priority in determining the appropriate policy.
"""

suggest_no_checkpoint_restart = """
Follow these instructions carefully:

1. If there is a timeout in the connection to storage — Suggest to RESTART THE JOB IMMEDIATELY.
2. If there is a broken pipe — Suggest to RESTART THE JOB IMMEDIATELY.
3. If there are Numerical instability or transient hardware issues — Suggest to RESTART THE JOB IMMEDIATELY.
4. If there are intermittent GPU initialization failures — Suggest to RESTART THE JOB IMMEDIATELY.
5. If there are intermittent GPU driver issues — Suggest to RESTART THE JOB IMMEDIATELY.
6. If there are race condition or resource busy errors — Suggest to RESTART THE JOB IMMEDIATELY.
7. If there are push/receive or expected-receive mismatches — Suggest to RESTART THE JOB IMMEDIATELY.
8. If there are Networking or InfiniBand-related issues — Suggest to RESTART THE JOB IMMEDIATELY.
9. If there are Node failures or infrastructure-level issues that can be resolved by restarting — Suggest to RESTART THE JOB IMMEDIATELY.
10. If there are Collective operation timeouts in NCCL communication — Suggest to RESTART THE JOB IMMEDIATELY.
"""

suggest_yes_checkpoint_stop = """
Follow these instructions carefully:

1. If there are explicit failures while saving checkpoints (paths or logs mentioning keywords such as checkpoint, ckpt, model.save, load_state_dict, or similar) due to permission, authentication, or access denied errors — Suggest to NOT RESTART THE JOB IMMEDIATELY. (High priority and critical instruction.)
2. If there are explicit errors indicating checkpointing issues related to the checkpoint destination directory (e.g., already exists, not empty, or inaccessible) — Suggest to NOT RESTART THE JOB IMMEDIATELY.
3. If restarting the job will not produce a new checkpoint (for example, the same errors are expected to reoccur) — Suggest to NOT RESTART THE JOB IMMEDIATELY.
4. If the cause is not explicitly clear or you are not 100% certain — Suggest to RESTART THE JOB IMMEDIATELY.
5. Ignore issues from missing files with randomize file path.
"""

suggest_yes_checkpoint_stop_extension = """
6. If the are permission, authentication, or access denied errors happens in the following cases: e.g., dataset loading or non-checkpoint I/O — Suggest to RESTART THE JOB IMMEDIATELY. Is a terminal cases but still the a new checkpoint produced.
"""

suggest_yes_checkpoint_restart = """
Follow these instructions carefully:

1. If there is a timeout in the connection to storage — Suggest to RESTART THE JOB IMMEDIATELY.
2. If there is a storage connection or accessibility issues — Suggest to RESTART THE JOB IMMEDIATELY.
3. If there are library or dependency loading failures — Suggest to RESTART THE JOB IMMEDIATELY.
4. If there is data loading broken pipe or exhaustion — Suggest to RESTART THE JOB IMMEDIATELY.
5. If there is a general communication failures — Suggest to RESTART THE JOB IMMEDIATELY.
6. If there is a collective operation timeouts in NCCL communication — Suggest to RESTART THE JOB IMMEDIATELY.
7. If there is a push/receive or expected-receive mismatches — Suggest to RESTART THE JOB IMMEDIATELY.
8. If there is a insufficient GPU memory, CPU memory, or disk resources — Suggest to RESTART THE JOB IMMEDIATELY.
9. If there is a data missing, data corruption, or bad formatting — Suggest to RESTART THE JOB IMMEDIATELY.
10. If there is a race conditions or resource busy states — Suggest to RESTART THE JOB IMMEDIATELY.
11. If there are numerical instability or transient hardware issues — Suggest to RESTART THE JOB IMMEDIATELY.
12. If there are Networking or InfiniBand connectivity issues — Suggest to RESTART THE JOB IMMEDIATELY.
13. If there are Communication issues between nodes — Suggest to RESTART THE JOB IMMEDIATELY, though other errors may take higher priority.
14. If there is a failed model saving due to connection interruptions — Suggest to RESTART THE JOB IMMEDIATELY.
15. If there are memory corruption or runtime errors such as "corrupted size vs. prev_size", "Aborted", or "double free or corruption" — Suggest to RESTART THE JOB IMMEDIATELY.
16. If there are node or infrastructure-level failures that can be resolved by restarting — Suggest to RESTART THE JOB IMMEDIATELY.
17. If the issues are secondary symptom or side effect of the issue - Suggest to RESTART THE JOB IMMEDIATELY. This instruction has higher priority.
18. If there are Collective operation timeouts in NCCL communication — Suggest to RESTART THE JOB IMMEDIATELY.
"""

proposed_solution_text = """
You are an expert on application logs. You will receive errors related to a training job and provide a unified explanation for resolving the issues.

Instructions:

1. Focus only on errors that are directly relevant and are the cause of the job failure.
2. Ignore errors that are not relevant or not the root cause.
3. Suggest configuration parameters or adjustments to solve the issue, if possible.
4. Increasing the NCCL timeout parameter is low priority. Only recommend it if there are no other actionable solutions.
5. Do not mention monitoring systems, system logs, other logs, or debugging tools.
6. The issue is not hardware-related, do not recommend checking hardware.
7. Pytorch NCCL watchdog errors have low priority; mention them only if no other issues exist.

Your output should be a clear, actionable explanation of the steps needed to resolve the failure.
"""

attribution_category_template = """
You are an expert in analyzing distributed training system logs.
You will receive error logs from large-scale applications.
Your task is to identify the most critical error and provide a clear, detailed attribution describing the main cause of failure.

Instructions:
1. Identify the primary issue (root cause) — not a side effect.
   - Errors such as watchdog collective operation timeouts, exit codes, or hang detections are secondary symptoms.
   - If they appear, find the underlying cause that triggered them.
2. Provide a descriptive attribution that explains what happened and why — include context about the failure,
   its nature, and any technical clues that support the attribution.
   - Keep it factual and concise (1-2 sentences).
3. If there is no main issue and only secondary issues are present, explicitly state that.
4. Do not include speculations, or notes beyond the final attribution.

Output Format:
'Attribution: <detailed description of the main issue, cause, and context>'
"""

attribution_infra_template = """
You are an expert in analyzing distributed training system logs.
You will receive error logs from large-scale applications running on distributed hardware systems (e.g., GPU, CPU, NIC, memory, or interconnects).
Your task is to identify the most critical hardware-related error and provide a clear, detailed attribution describing the main cause of failure.

Instructions:
1. Identify the primary hardware issue (root cause) — not a side effect.
   - Errors such as watchdog collective operation timeouts, exit codes, or hang detections are secondary symptoms.
   - If they appear, find the underlying hardware or communication failure that triggered them.
2. Provide a descriptive attribution that explains what happened and why — include context about the failure,
   its nature, and any technical clues that support the attribution.
   - Keep it factual and concise (1-2 sentences).
3. Do not include speculations, or notes beyond the final attribution.

Output Format:
'Attribution: <detailed description of the main hardware issue, cause, and context>'
"""

template_application_crash_check = """
You will get log lines from an AI training job. Determine if the job **failed** or not.
If the job failed, return 'yes'. If it did not fail, return 'no'.

Instructions:
1. Return “yes” only if you clearly see explicit errors or failure indicators showing that the job failed or crashed.
2. If you explicitly identify that the training finished, return “no”.
3. If you see that the job continues to execute after the error, return “no”.
4. If you see that the training is stuck, return “yes”.
5. If there are no explicit errors, return “no”.

Do not add any additional information, headers, or footers.

Your answer must be exactly 'yes' or 'no'.
"""

template_application_cause_check = """
You are an expert in analyzing application logs. You will receive the errors of a job running across multiple nodes.
Your task is to check whether the cause exists in the errors or not"

Instructions:
1. If the exact cause is specified, reply with "yes".
2. If the exact cause is not specified, reply with "no".
3. If the errors are only a secondary symptom of the issue is present, suggest "no".
4. If you are no sure 100%, reply with "yes".

Do not add any additional information, headers, or footers.

Your answer must be exactly 'yes' or 'no'.
"""

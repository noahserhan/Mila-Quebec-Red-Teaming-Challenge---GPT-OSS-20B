# Mila’s Submission to Red-Teaming Challenge - OpenAI gpt-oss-20b
LM Studio was used to run all these experiments. These were the parameters that were set:

```python
"temperature": 0.8,
"reasoning_level": "high",
"max_output_tokens": 25031,
"top_p": 0.8,
"top_k":40,
"repeat_penalty": 1.1,
"min_p sampling": 0.05
```

## Setup the environment

```python
conda create -n gpt_oss python=3.12
conda activate gpt_oss
pip install -r requirements.txt
```

## Reward Hacking: Admin Role Facilitates Bypassing of Safety Policies

The notebook `openai_tag_eg.ipynb` demostrates this attack. You can use the given conda environment to run this self contained notebook. 

Please note that you might have to rerun the cells multiple times (upto 10 times) to get the required behaviour. Although we would prefer that this is run using LM Studio.

## Data Exfiltration: Corporate Assistant Leaks Sensitive Data

To run this attack, you need to use the LM Studio. Replace the `mcp.json` file for a chat window with the contents of `mcp-config.json` file and place the `fast_mcp_server.py` file in the `.lmstudio` directory. Now you can connect the MCP server with the LM Studio chat window. Next use the conversation in the `finding_admin_pri.json` to replicate the attack.

## Data Exfiltration: Environment String Injection Attack Leads to Information Leak

The notebook `openai_tag_eg.ipynb` demostrates this attack. You can use the given conda environment to run this self contained notebook. 

## Loading the Conversation File

The conversation file can be loaded using the following 
```python
python load_conversation.py --filename <path to the findings file>
```
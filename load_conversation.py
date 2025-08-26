import json
import re
import argparse
from typing import List, Dict, Any

def parse_conversation_json(file_path: str) -> None:
    """
    Parse a conversation JSON file and display messages with clear headers.
    
    Args:
        file_path (str): Path to the JSON file containing the conversation
    """
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extract the output string
        if 'harmony_response_walkthroughs' not in data: #read key harmony_response_walkthroughs
            print("Error: JSON file must contain an 'output' key")
            return
        
        conversation_text = data["harmony_response_walkthroughs"][0]
        
        # Parse the conversation
        messages = parse_conversation_text(conversation_text)
        
        # Display the parsed messages
        display_messages(messages)
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"Error: {e}")

def parse_conversation_text(text: str) -> List[Dict[str, Any]]:
    """
    Parse the conversation text into individual messages.
    
    Args:
        text (str): Raw conversation text from the JSON output
        
    Returns:
        List[Dict[str, Any]]: List of parsed message dictionaries
    """
    messages = []
    
    # Split by message boundaries
    message_pattern = r'<\|start\|>(.*?)<\|end\|>|<\|start\|>(.*?)<\|call\|>'
    matches = re.findall(message_pattern, text, re.DOTALL)
    
    for match in matches:
        content = match[0] if match[0] else match[1]
        if not content.strip():
            continue
            
        message = parse_single_message(content.strip())
        if message:
            messages.append(message)
    
    return messages

def parse_single_message(content: str) -> Dict[str, Any]:
    """
    Parse a single message content into structured data.
    
    Args:
        content (str): Content of a single message
        
    Returns:
        Dict[str, Any]: Parsed message data
    """
    message = {
        'type': 'unknown',
        'content': '',
        'channel': None,
        'to': None,
        'tool_name': None,
        'constrain': None
    }
    
    # Parse system messages
    if content.startswith('system<|message|>'):
        message['type'] = 'system'
        message['content'] = content.replace('system<|message|>', '').strip()
    
    # Parse developer messages
    elif content.startswith('developer<|message|>'):
        message['type'] = 'developer'
        message['content'] = content.replace('developer<|message|>', '').strip()
    
    # Parse user messages
    elif content.startswith('user<|message|>'):
        message['type'] = 'user'
        message['content'] = content.replace('user<|message|>', '').strip()
    
    # Parse assistant messages
    elif content.startswith('assistant<|channel|>'):
        # Extract channel and other components
        pattern = r'assistant<\|channel\|>([^<]*?)(?:\s+to=([^<\s]+))?(?:\s+<\|constrain\|>([^<]+))?<\|message\|>(.*)'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            channel = match.group(1).strip()
            to_target = match.group(2)
            constrain = match.group(3)
            msg_content = match.group(4).strip()
            
            message['channel'] = channel
            message['to'] = to_target
            message['constrain'] = constrain
            message['content'] = msg_content
            
            # Determine message type based on channel and content
            if channel == 'analysis' or 'analysis' in channel:
                message['type'] = 'assistant_cot'
            elif to_target and ('functions' in to_target or constrain == 'json'):
                message['type'] = 'assistant_tool'
            elif channel == 'final' or 'final' in channel:
                message['type'] = 'assistant_response'
            else:
                message['type'] = 'assistant_other'
    
    # Parse tool output messages
    elif re.match(r'^[a-zA-Z_]+\.[a-zA-Z_]+\s+to=', content):
        pattern = r'^([a-zA-Z_]+)\.([a-zA-Z_]+)\s+to=([^<]+)<\|channel\|>([^<]+)<\|message\|>(.*)'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            message['type'] = 'tool_response'
            message['tool_name'] = f"{match.group(1)}.{match.group(2)}"
            message['to'] = match.group(3).strip()
            message['channel'] = match.group(4).strip()
            message['content'] = match.group(5).strip()
    
    return message if message['content'] else None

def display_messages(messages: List[Dict[str, Any]]) -> None:
    """
    Display parsed messages with clear headers and formatting.
    
    Args:
        messages (List[Dict[str, Any]]): List of parsed messages
    """
    if not messages:
        print("No messages found in the conversation.")
        return
    
    print("=" * 80)
    print("CONVERSATION BREAKDOWN")
    print("=" * 80)
    print()
    
    message_counter = 1
    
    for message in messages:
        # Determine header based on message type
        if message['type'] == 'system':
            header = "🔧 SYSTEM MESSAGE"
        elif message['type'] == 'developer':
            header = "👩‍💻 DEVELOPER MESSAGE"
        elif message['type'] == 'user':
            header = "👤 USER MESSAGE"
        elif message['type'] == 'assistant_cot':
            header = "🧠 ASSISTANT CHAIN OF THOUGHT"
            if message['channel']:
                header += f" ({message['channel']})"
        elif message['type'] == 'assistant_tool':
            header = "🔨 ASSISTANT TOOL USE"
            if message['to']:
                header += f" → {message['to']}"
        elif message['type'] == 'tool_response':
            header = "⚙️ TOOL RESPONSE"
            if message['tool_name']:
                header += f" ({message['tool_name']})"
        elif message['type'] == 'assistant_response':
            header = "🤖 ASSISTANT RESPONSE"
        else:
            header = f"❓ {message['type'].upper()}"
        
        # Print message header
        print(f"{message_counter}. {header}")
        print("-" * len(f"{message_counter}. {header}"))
        
        # Print metadata if present
        metadata = []
        if message['channel']:
            metadata.append(f"Channel: {message['channel']}")
        if message['to']:
            metadata.append(f"To: {message['to']}")
        if message['constrain']:
            metadata.append(f"Format: {message['constrain']}")
        
        if metadata:
            print(f"Metadata: {' | '.join(metadata)}")
            print()
        
        # Print content
        content = message['content']
        if len(content) > 500:
            print(content[:500] + "...")
            print(f"[Content truncated - {len(content)} characters total]")
        else:
            print(content)
        
        print()
        print("-" * 80)
        print()
        
        message_counter += 1
    
    print(f"Total messages parsed: {len(messages)}")

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description="Load the conversation file."
    )

    # basic file IO
    parser.add_argument( "--filename",
                        type=str,
                        required=True,
                        help="Path to input file")
    args = parser.parse_args()

    parse_conversation_json(args.filename)

import os
import pandas as pd
import re
import json

# Define directories
base_dirs = [
    r"C:\Users\pablo\Desktop\initial experiments\cognition\condition 1\cog_greene_c1_1",
    r"C:\Users\pablo\Desktop\initial experiments\cognition\condition 1\cog_suter_c1_1",
    r"C:\Users\pablo\Desktop\initial experiments\cognition\condition 2\cog_greene_c2_1",
    r"C:\Users\pablo\Desktop\initial experiments\cognition\condition 2\cog_suter_c2_1",
    r"C:\Users\pablo\Desktop\initial experiments\cognition\control\cog_greene_control_1",
    r"C:\Users\pablo\Desktop\initial experiments\cognition\control\cog_suter_control_1",
    r"C:\Users\pablo\Desktop\initial experiments\deliberation\deliberation_greene_1",
    r"C:\Users\pablo\Desktop\initial experiments\deliberation\deliberation_suter_1"
]

# Define output file
output_file = r"C:\Users\pablo\Desktop\experiment_results.csv"

def extract_data_from_text(text):
    """Extract relevant fields from text."""
    try:
        # Extract last occurrence of YES or NO as the response
        response_match = re.findall(r'\b(YES|NO)\b', text, re.IGNORECASE)
        response = response_match[-1].upper() if response_match else "UNKNOWN"
        
        # Extract metadata JSON block
        metadata_match = re.search(r'Metadata:\s*(\{.*?\})', text, re.DOTALL)
        metadata = json.loads(metadata_match.group(1)) if metadata_match else {}
        
        # Extract token probability details
        logprobs_match = re.findall(r'Token:\s*(\S+)\nLog Probability:\s*([\-\d\.]+)\nTop 5 Alternatives:', text)
        alt_tokens = re.findall(r'Top 5 Alternatives:\n(.*?)(?:\n\n|$)', text, re.DOTALL)
        
        token_probs = {}
        if response_match:
            response_token = response_match[-1]
            for token, prob in logprobs_match:
                if token.upper() == response_token:
                    token_probs['probability'] = float(prob)
                    
                    if alt_tokens:
                        alternatives = re.findall(r'\s*(\S+):\s*([\-\d\.]+)', alt_tokens[0])
                        for i, (alt, alt_prob) in enumerate(alternatives[:5]):
                            token_probs[f'alt{i+1}'] = alt
                            token_probs[f'alt{i+1}_prob'] = float(alt_prob)
                    break
        
        return response, token_probs, metadata.get("usage", {}).get("completion_tokens", 0)
    except Exception as e:
        print(f"Error extracting data: {e}")
        return "UNKNOWN", {}, 0

data = []
participant_id = 1

for base_dir in base_dirs:
    if not os.path.exists(base_dir):
        print(f"Skipping missing directory: {base_dir}")
        continue
    
    experiment_type = "cognition" if "cognition" in base_dir else "deliberation"
    condition = "control" if "control" in base_dir else ("condition 1" if "condition 1" in base_dir else "condition 2" if "condition 2" in base_dir else "deliberation")
    
    for filename in os.listdir(base_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(base_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                
                scenario = "suter" if "suter" in filename else "greene"
                match = re.match(r"scenario(\d+)prompt(\d+)", filename)
                if not match:
                    print(f"Skipping file with unrecognized format: {filename}")
                    continue
                scenario_number, prompt_number = match.groups()
                
                response, token_probs, total_tokens = extract_data_from_text(text)
                
                row = {
                    "Id": participant_id,
                    "Scenario": scenario,
                    "Scenario Number": int(scenario_number),
                    "Prompt Number": int(prompt_number),
                    "Experiment Type": experiment_type,
                    "Condition": condition,
                    "Response": response,
                    "Probability": token_probs.get("probability", ""),
                    "Alt1": token_probs.get("alt1", ""),
                    "Alt1 Prob": token_probs.get("alt1_prob", ""),
                    "Alt2": token_probs.get("alt2", ""),
                    "Alt2 Prob": token_probs.get("alt2_prob", ""),
                    "Alt3": token_probs.get("alt3", ""),
                    "Alt3 Prob": token_probs.get("alt3_prob", ""),
                    "Alt4": token_probs.get("alt4", ""),
                    "Alt4 Prob": token_probs.get("alt4_prob", ""),
                    "Alt5": token_probs.get("alt5", ""),
                    "Alt5 Prob": token_probs.get("alt5_prob", ""),
                    "Total Tokens": total_tokens
                }
                
                if "cognition" in base_dir and "control" not in base_dir:
                    row["Variation"] = "1" if "condition 1" in base_dir else "2"
                else:
                    row["Variation"] = ""
                
                data.append(row)
                participant_id += 1
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

# Save to CSV
df = pd.DataFrame(data)
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"CSV saved at: {output_file}")

import os

def load_cornell_movie_dialogues(data_dir):
    """
    Load the Cornell Movie Dialogues Corpus.
    """
    dialogues = []
    with open(os.path.join(data_dir, "movie_lines.txt"), "r", encoding="iso-8859-1") as f:
        lines = f.readlines()
    
    with open(os.path.join(data_dir, "movie_conversations.txt"), "r", encoding="iso-8859-1") as f:
        conversations = f.readlines()

    # Parse lines and conversations
    line_dict = {}
    for line in lines:
        parts = line.split(" +++$+++ ")
        line_id = parts[0]
        text = parts[-1].strip()
        line_dict[line_id] = text

    for conv in conversations:
        parts = conv.split(" +++$+++ ")
        line_ids = eval(parts[-1])  # Convert string to list
        dialogue = [line_dict[line_id] for line_id in line_ids]
        dialogues.append(dialogue)

    return dialogues

# Example usage
data_dir = "path_to_cornell_movie_dialogues"
dialogues = load_cornell_movie_dialogues(data_dir)
for dialogue in dialogues[:5]:
    print("\n".join(dialogue))
    print("---")
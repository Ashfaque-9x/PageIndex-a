import json
from litellm import completion

# -----------------------------
# Load PageIndex Tree
# -----------------------------
with open(
    "results/Matter Around Us_structure.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

tree = data["structure"]

# -----------------------------
# Flatten nodes minimally
# -----------------------------
all_nodes = []

def flatten_tree(nodes, path=""):
    for node in nodes:
        title = node.get("title", "")

        current_path = f"{path} > {title}" if path else title

        entry = {
            "path": current_path,
            "summary": node.get("summary", ""),
            "text": node.get("text", "")
        }

        all_nodes.append(entry)

        if "nodes" in node:
            flatten_tree(node["nodes"], current_path)

flatten_tree(tree)

# -----------------------------
# Retrieval via LLM
# -----------------------------
def retrieve_relevant_nodes(question):

    catalog = []

    for idx, node in enumerate(all_nodes):
        catalog.append(f"""
        NODE {idx}

        PATH:
        {node['path']}

        SUMMARY:
        {node['summary']}

        TEXT PREVIEW:
        {node['text'][:1000]}
        """)

    retrieval_prompt = f"""
    You are a retrieval engine.

    Select the MOST relevant node IDs for answering the question.

    Return ONLY valid JSON.

    Example:
    [0]
    [1,2]
    
    Do not explain.
    Do not use markdown.

    Question:
    {question}

    Available Nodes:
    {catalog}
    """

    response = completion(
        model="ollama/qwen2.5:7b",
        messages=[
            {"role": "user", "content": retrieval_prompt}
        ],
        api_base="http://localhost:11434",
        api_key="ollama"
    )

    content = response["choices"][0]["message"]["content"]

    try:
        ids = json.loads(content)
    except Exception as e:
        print("Retrieval parsing failed:", content)
        ids = []

    return ids


# -----------------------------
# QA
# -----------------------------
while True:

    question = input("\nAsk Question: ")

    if question.lower() == "exit":
        break

    node_ids = retrieve_relevant_nodes(question)

    context = ""

    for idx in node_ids:
        if idx < len(all_nodes):

            node = all_nodes[idx]

            context += f"""
            PATH:
            {node['path']}

            CONTENT:
            {node['text']}
            """

    answer_prompt = f"""
    Answer the question using ONLY the provided context.

    Context:
    {context}

    Question:
    {question}
    """

    response = completion(
        model="ollama/qwen2.5:7b",
        messages=[
            {"role": "user", "content": answer_prompt}
        ],
        api_base="http://localhost:11434",
        api_key="ollama"
    )

    answer = response["choices"][0]["message"]["content"]

    print("\nAnswer:\n")
    print(answer)
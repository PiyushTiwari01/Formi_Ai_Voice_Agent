from transformers import GPT2Tokenizer

# Load the tokenizer globally (only once)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

def chunk_content(data_list, max_tokens=800):
    """
    Splits a list of data items into chunks based on GPT2 token limits.
    
    Args:
        data_list (List[str]): List of strings (or dicts, which will be stringified) to chunk.
        max_tokens (int): Maximum tokens per chunk. Default is 800.
    
    Returns:
        List[List[str]]: List of chunks, each under max_tokens.
    """
    chunks = []
    chunk = []
    token_count = 0

    for item in data_list:
        tokens = tokenizer.encode(str(item))  # Convert item to token list
        if token_count + len(tokens) <= max_tokens:
            chunk.append(item)
            token_count += len(tokens)
        else:
            chunks.append(chunk)
            chunk = [item]
            token_count = len(tokens)

    if chunk:
        chunks.append(chunk)

    return chunks

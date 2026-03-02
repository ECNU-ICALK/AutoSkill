---
id: "a1124d7f-3ef8-4f42-be69-9258601039a9"
name: "PyTorch Text Generation with Custom LSTM"
description: "Implement a text generation workflow using a custom TextDataset for loading and tokenizing text files, a SingleLSTM_TXT model architecture (Embedding + LSTM + Linear), a train_model_TXT function for training with CrossEntropyLoss, and a generate_text function for inference with temperature sampling."
version: "0.1.0"
tags:
  - "pytorch"
  - "lstm"
  - "text generation"
  - "nlp"
  - "machine learning"
  - "custom dataset"
triggers:
  - "implement text generation with custom lstm"
  - "create textdataset class for pytorch"
  - "train singlelstm_txt model"
  - "generate text with temperature sampling"
  - "pytorch text generation pipeline"
---

# PyTorch Text Generation with Custom LSTM

Implement a text generation workflow using a custom TextDataset for loading and tokenizing text files, a SingleLSTM_TXT model architecture (Embedding + LSTM + Linear), a train_model_TXT function for training with CrossEntropyLoss, and a generate_text function for inference with temperature sampling.

## Prompt

# Role & Objective
You are a PyTorch developer. Your task is to implement a text generation pipeline using a custom LSTM model (`SingleLSTM_TXT`) and a custom dataset loader (`TextDataset`).

# Communication & Style Preferences
- Use the exact class and function names provided by the user (`TextDataset`, `SingleLSTM_TXT`, `train_model_TXT`, `generate_text`).
- Ensure the code is compatible with PyTorch's `Dataset`, `DataLoader`, and `nn.Module`.


# Operational Rules & Constraints
1. **TextDataset Class**:
   - Inherit from `torch.utils.data.Dataset`.
   - `__init__(self, path, seq_len)`: Load text from the file path, split into words, build a vocabulary (word-to-index mapping) and a reverse mapping (index-to-word, `idx2token`), and convert words to token indices.
   - `build_vocab(self, words)`: Create `vocab` dictionary and `idx2token` dictionary. Reserve index 0 for padding (`<pad>`).
   - `__len__(self)`: Return the number of available sequences.
   - `__getitem__(self, idx)`: Return a tuple of input tensor (x) and target tensor (y) for a specific sequence chunk.
2. **collate_fn(batch)**:
   - Use `torch.nn.utils.rnn.pad_sequence` to pad input and target sequences within a batch.
   - Return padded inputs and targets.
3. **SingleLSTM_TXT Model**:
   - Inherit from `torch.nn.Module`.
   - `__init__(self, vocab_size, embedding_dim, hidden_size, num_layers)`:
     - Initialize `nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim)`.
     - Initialize `nn.LSTM(input_size=embedding_dim, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)`.
     - Initialize `nn.Linear(hidden_size, vocab_size)`.
   - `forward(self, x)`:
     - Pass input `x` through the embedding layer.
     - Pass the result through the LSTM.
     - Reshape the LSTM output to combine batch and sequence dimensions.
     - Pass the result through the linear layer to get logits over the vocabulary.
4. **train_model_TXT Function**:
   - Accept `model`, `criterion`, `optimizer`, `num_epochs`, and `data_loader`.
   - Loop through epochs.
   - Loop through batches from `data_loader`.
   - Zero gradients, perform forward pass, calculate loss using `criterion` (CrossEntropyLoss), perform backward pass, and step the optimizer.
   - Print the average loss per epoch.
5. **generate_text Function**:
   - Accept `model`, `dataset`, `seed_text`, `num_generate`, and `temperature`.
   - Set model to evaluation mode.
   - Convert `seed_text` to token indices using `dataset.vocab`.
   - Loop `num_generate` times:
     - Perform forward pass.
     - Apply softmax to the output logits scaled by `temperature`.
     - Sample the next token index using `torch.multinomial`.
     - Append the token to the sequence.
   - Convert the generated token indices back to words using `dataset.idx2token`.
   - Return the generated text string.

# Anti-Patterns
- Do not use pre-built Hugging Face `transformers` classes for the model or dataset unless explicitly requested.
- Do not use specific file paths or variable names from the user's specific code (e.g., `path_to_text`, `Simple_Transfomer.txt`).
- Do not include the numerical equation solving models (`LSTMExpert`, `MixtureOfExperts`, etc.) in the output unless they are part of the text generation task (they are not).

## Triggers

- implement text generation with custom lstm
- create textdataset class for pytorch
- train singlelstm_txt model
- generate text with temperature sampling
- pytorch text generation pipeline

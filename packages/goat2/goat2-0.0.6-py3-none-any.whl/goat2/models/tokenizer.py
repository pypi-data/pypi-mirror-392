"""
Tokenizer for text processing optimized for word embedding models like Word2Vec and GloVe.
"""

import re
import string
import unicodedata
from typing import List, Dict, Set, Tuple, Optional, Callable, Union, Iterator, Any
import logging
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords

# Add PyTorch import
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


class Tokenizer:
    """Flexible tokenizer for text preprocessing and tokenization."""
    
    def __init__(
        self,
        lowercase: bool = True,
        remove_punctuation: bool = True,
        remove_digits: bool = False,
        remove_stopwords: bool = False,
        stem: bool = False,
        lemmatize: bool = False,
        min_token_length: int = 1,
        max_token_length: Optional[int] = None,
        language: str = 'english',
        custom_stopwords: Optional[Set[str]] = None,
        custom_filters: Optional[List[Callable[[str], str]]] = None,
        keep_n_grams: Optional[List[int]] = None,
        n_gram_delimiter: str = '_',
        # New parameters for special tokens
        pad_token: str = "<pad>",
        unk_token: str = "<unk>",
        bos_token: str = "<bos>",
        eos_token: str = "<eos>",
        mask_token: str = "<mask>",
        special_tokens: Optional[List[str]] = None
    ):
        """
        Initialize the tokenizer with specified preprocessing options.
        
        Args:
            lowercase: Convert text to lowercase
            remove_punctuation: Remove punctuation
            remove_digits: Remove numeric digits
            remove_stopwords: Remove common stopwords
            stem: Apply stemming (Porter stemmer)
            lemmatize: Apply lemmatization (WordNet lemmatizer)
            min_token_length: Minimum length for a token to be kept
            max_token_length: Maximum length for a token to be kept (None = no limit)
            language: Language for stopwords and other language-specific processing
            custom_stopwords: Additional stopwords to remove
            custom_filters: List of custom filter functions for additional preprocessing
            keep_n_grams: List of n-gram sizes to generate (e.g., [2, 3] for bigrams and trigrams)
            n_gram_delimiter: Character to join n-gram components
            pad_token: Token used for padding sequences to equal length
            unk_token: Token used for unknown words
            bos_token: Beginning of sequence token
            eos_token: End of sequence token
            mask_token: Token used for masked language modeling
            special_tokens: Additional special tokens to include
        """
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_digits = remove_digits
        self.remove_stopwords = remove_stopwords
        self.stem = stem
        self.lemmatize = lemmatize
        self.min_token_length = min_token_length
        self.max_token_length = max_token_length
        self.language = language
        self.custom_filters = custom_filters or []
        self.keep_n_grams = keep_n_grams or []
        self.n_gram_delimiter = n_gram_delimiter
        
        # Set up stopwords
        if remove_stopwords:
            self.stopwords = set(stopwords.words(language))
            if custom_stopwords:
                self.stopwords.update(custom_stopwords)
        else:
            self.stopwords = set()
            if custom_stopwords:
                self.stopwords = custom_stopwords
        
        # Set up stemmers and lemmatizers if needed
        if stem:
            self.stemmer = PorterStemmer()
        
        if lemmatize:
            self.lemmatizer = WordNetLemmatizer()
        
        # Set up punctuation translation table
        if remove_punctuation:
            self.punctuation_table = str.maketrans('', '', string.punctuation)
        
        # Set up digit translation table
        if remove_digits:
            self.digit_table = str.maketrans('', '', string.digits)
        
        # Initialize special tokens
        self.pad_token = pad_token
        self.unk_token = unk_token
        self.bos_token = bos_token
        self.eos_token = eos_token
        self.mask_token = mask_token
        self.default_special_tokens = [pad_token, unk_token, bos_token, eos_token, mask_token]
        self.special_tokens = self.default_special_tokens + (special_tokens or [])
        
        # Dictionary to store token-to-id and id-to-token mappings
        self.token_to_id = {}
        self.id_to_token = {}
        
        # For handling unknown tokens
        self.unk_token_id = None
        self.pad_token_id = None
    
    def _preprocess_text(self, text: str) -> str:
        """Apply preprocessing steps to text."""
        # Apply lowercasing
        if self.lowercase:
            text = text.lower()
        
        # Apply custom filters
        for filter_fn in self.custom_filters:
            text = filter_fn(text)
        
        # Remove punctuation
        if self.remove_punctuation:
            text = text.translate(self.punctuation_table)
        
        # Remove digits
        if self.remove_digits:
            text = text.translate(self.digit_table)
        
        return text
    
    def _process_token(self, token: str) -> str:
        """Apply token-level processing (stemming, lemmatization)."""
        # Apply stemming
        if self.stem:
            token = self.stemmer.stem(token)
        
        # Apply lemmatization
        if self.lemmatize:
            token = self.lemmatizer.lemmatize(token)
        
        return token
    
    def _is_valid_token(self, token: str) -> bool:
        """Check if token meets criteria for inclusion."""
        # Check minimum length
        if len(token) < self.min_token_length:
            return False
        
        # Check maximum length
        if self.max_token_length and len(token) > self.max_token_length:
            return False
        
        # Check if token is a stopword
        if token in self.stopwords:
            return False
        
        # Remove tokens that are just whitespace
        if token.strip() == '':
            return False
        
        return True
    
    def _generate_n_grams(self, tokens: List[str]) -> List[str]:
        """Generate n-grams from tokens."""
        result = tokens.copy()
        
        for n in self.keep_n_grams:
            if n < 2 or n > len(tokens):
                continue
                
            for i in range(len(tokens) - n + 1):
                n_gram = self.n_gram_delimiter.join(tokens[i:i+n])
                result.append(n_gram)
        
        return result
    
    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize a single text string according to configured options.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of processed tokens
        """
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Apply preprocessing
        text = self._preprocess_text(text)
        
        # Tokenize into words
        tokens = word_tokenize(text, language=self.language)
        
        # Process tokens
        processed_tokens = []
        for token in tokens:
            # Apply token-level processing
            processed = self._process_token(token)
            
            # Check if token is valid
            if self._is_valid_token(processed):
                processed_tokens.append(processed)
        
        # Generate n-grams if specified
        if self.keep_n_grams:
            processed_tokens = self._generate_n_grams(processed_tokens)
        
        return processed_tokens
    
    def tokenize_texts(self, texts: List[str]) -> List[List[str]]:
        """
        Tokenize a list of texts.
        
        Args:
            texts: List of texts to tokenize
            
        Returns:
            List of lists of tokens
        """
        return [self.tokenize_text(text) for text in texts]
    
    def tokenize_into_sentences(self, text: str) -> List[List[str]]:
        """
        Tokenize text into sentences, then tokenize each sentence into words.
        
        Args:
            text: Input text
            
        Returns:
            List of lists of tokens, where each inner list represents a sentence
        """
        # Split into sentences
        sentences = sent_tokenize(text, language=self.language)
        
        # Tokenize each sentence
        return self.tokenize_texts(sentences)
    
    def build_vocab(
        self, 
        texts: List[str], 
        min_count: int = 5, 
        max_vocab_size: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Build vocabulary from texts.
        
        Args:
            texts: List of texts to process
            min_count: Minimum occurrence count to include a token
            max_vocab_size: Maximum vocabulary size (None = no limit)
            
        Returns:
            Dictionary mapping tokens to their indices
        """
        # Tokenize all texts
        all_tokens = []
        for text in texts:
            all_tokens.extend(self.tokenize_text(text))
        
        # Count tokens
        counter = Counter(all_tokens)
        
        # Filter by min_count
        filtered_tokens = [(token, count) for token, count in counter.items() 
                           if count >= min_count]
        
        # Sort by frequency (most frequent first)
        sorted_tokens = sorted(filtered_tokens, key=lambda x: x[1], reverse=True)
        
        # Limit vocab size if specified, reserving space for special tokens
        if max_vocab_size:
            available_space = max_vocab_size - len(self.special_tokens)
            sorted_tokens = sorted_tokens[:available_space]
        
        # Create word to index mapping, giving priority to special tokens
        vocab = {}
        idx = 0
        
        # First add special tokens
        for token in self.special_tokens:
            vocab[token] = idx
            idx += 1
            
        # Then add the rest of the tokens
        for token, _ in sorted_tokens:
            if token not in vocab:  # Skip if token is already in vocab (e.g., as a special token)
                vocab[token] = idx
                idx += 1
        
        # Store the mappings
        self.token_to_id = vocab
        self.id_to_token = {idx: token for token, idx in vocab.items()}
        
        # Store special token IDs for convenience
        self.pad_token_id = vocab.get(self.pad_token)
        self.unk_token_id = vocab.get(self.unk_token)
        
        return vocab
    
    def prepare_for_word_embeddings(
        self, 
        texts: List[str],
        min_count: int = 5,
        max_vocab_size: Optional[int] = None
    ) -> Tuple[List[List[str]], Dict[str, int]]:
        """
        Prepare texts for word embedding models like Word2Vec or GloVe.
        
        Args:
            texts: List of raw text strings
            min_count: Minimum occurrence count to include a token
            max_vocab_size: Maximum vocabulary size (None = no limit)
            
        Returns:
            Tuple of (tokenized_texts, vocabulary)
        """
        # Tokenize texts
        tokenized_texts = self.tokenize_texts(texts)
        
        # Count all tokens
        counter = Counter()
        for tokens in tokenized_texts:
            counter.update(tokens)
        
        # Filter by min_count
        filtered_tokens = [(token, count) for token, count in counter.items() 
                          if count >= min_count]
        
        # Sort by frequency
        sorted_tokens = sorted(filtered_tokens, key=lambda x: x[1], reverse=True)
        
        # Limit vocab size if specified, reserving space for special tokens
        if max_vocab_size:
            available_space = max_vocab_size - len(self.special_tokens)
            sorted_tokens = sorted_tokens[:available_space]
        
        # Create vocab, giving priority to special tokens
        vocab = {}
        idx = 0
        
        # First add special tokens
        for token in self.special_tokens:
            vocab[token] = idx
            idx += 1
            
        # Then add the rest of the tokens
        for token, _ in sorted_tokens:
            if token not in vocab:  # Skip if token is already in vocab
                vocab[token] = idx
                idx += 1
        
        # Store the mappings
        self.token_to_id = vocab
        self.id_to_token = {idx: token for token, idx in vocab.items()}
        
        # Store special token IDs for convenience
        self.pad_token_id = vocab.get(self.pad_token)
        self.unk_token_id = vocab.get(self.unk_token)
        
        return tokenized_texts, vocab
    
    # New token conversion methods
    def convert_tokens_to_ids(self, tokens: List[str]) -> List[int]:
        """
        Convert a list of tokens to their corresponding IDs.
        
        Args:
            tokens: List of tokens to convert
            
        Returns:
            List of token IDs
        """
        if not self.token_to_id:
            raise ValueError("Vocabulary not built yet. Call build_vocab() or prepare_for_word_embeddings() first.")
            
        return [self.token_to_id.get(token, self.unk_token_id) for token in tokens]
    
    def convert_ids_to_tokens(self, ids: List[int]) -> List[str]:
        """
        Convert a list of token IDs back to tokens.
        
        Args:
            ids: List of token IDs to convert
            
        Returns:
            List of tokens
        """
        if not self.id_to_token:
            raise ValueError("Vocabulary not built yet. Call build_vocab() or prepare_for_word_embeddings() first.")
            
        return [self.id_to_token.get(idx, self.unk_token) for idx in ids]
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """
        Tokenize and convert text to token IDs.
        
        Args:
            text: Text to encode
            add_special_tokens: Whether to add BOS/EOS tokens
            
        Returns:
            List of token IDs
        """
        tokens = self.tokenize_text(text)
        
        if add_special_tokens:
            tokens = [self.bos_token] + tokens + [self.eos_token]
            
        return self.convert_tokens_to_ids(tokens)
    
    def decode(self, ids: List[int], skip_special_tokens: bool = False) -> str:
        """
        Convert token IDs back to text.
        
        Args:
            ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens in output
            
        Returns:
            Decoded text
        """
        tokens = self.convert_ids_to_tokens(ids)
        
        if skip_special_tokens:
            tokens = [token for token in tokens if token not in self.special_tokens]
            
        return " ".join(tokens)
    
    def batch_encode(self, texts: List[str], add_special_tokens: bool = False) -> List[List[int]]:
        """
        Encode a batch of texts to token IDs.
        
        Args:
            texts: List of texts to encode
            add_special_tokens: Whether to add BOS/EOS tokens
            
        Returns:
            List of lists of token IDs
        """
        return [self.encode(text, add_special_tokens) for text in texts]
    
    # PyTorch integration methods
    def encode_as_tensor(
        self, 
        text: str, 
        add_special_tokens: bool = False, 
        return_tensors: str = 'pt'
    ) -> Union[List[int], 'torch.Tensor']:
        """
        Encode text and return as PyTorch tensor if requested.
        
        Args:
            text: Text to encode
            add_special_tokens: Whether to add BOS/EOS tokens
            return_tensors: Output format ('pt' for PyTorch tensor, None for list)
            
        Returns:
            Token IDs as list or PyTorch tensor
        """
        ids = self.encode(text, add_special_tokens)
        
        if return_tensors == 'pt':
            if not TORCH_AVAILABLE:
                raise ImportError("PyTorch is not installed. Install it with 'pip install torch'.")
            return torch.tensor(ids)
        
        return ids
    
    def batch_encode_as_tensors(
        self, 
        texts: List[str], 
        add_special_tokens: bool = False,
        padding: bool = False,
        truncation: bool = False,
        max_length: Optional[int] = None,
        return_attention_mask: bool = False,
        return_tensors: str = 'pt'
    ) -> Dict[str, Union[List, 'torch.Tensor']]:
        """
        Encode a batch of texts with padding and attention masks.
        
        Args:
            texts: List of texts to encode
            add_special_tokens: Whether to add BOS/EOS tokens
            padding: Whether to pad sequences to equal length
            truncation: Whether to truncate sequences longer than max_length
            max_length: Maximum sequence length (if truncation is True)
            return_attention_mask: Whether to return attention mask
            return_tensors: Output format ('pt' for PyTorch tensor, None for list)
            
        Returns:
            Dictionary with 'input_ids' and optionally 'attention_mask'
        """
        # Encode all texts
        encoded_texts = [self.encode(text, add_special_tokens) for text in texts]
        
        # Handle truncation if requested
        if truncation and max_length:
            encoded_texts = [ids[:max_length] for ids in encoded_texts]
        
        # Get the length of each sequence for padding and attention mask
        seq_lengths = [len(ids) for ids in encoded_texts]
        
        # Handle padding if requested
        if padding:
            # Determine padding length
            if max_length:
                padding_length = max_length
            else:
                padding_length = max(seq_lengths)
            
            # Pad sequences
            padded_texts = []
            attention_masks = []
            
            for ids in encoded_texts:
                # Calculate padding needed
                padding_needed = padding_length - len(ids)
                
                # Pad with pad token ID
                padded_ids = ids + [self.pad_token_id] * padding_needed
                padded_texts.append(padded_ids)
                
                # Create attention mask (1 for actual tokens, 0 for padding)
                if return_attention_mask:
                    mask = [1] * len(ids) + [0] * padding_needed
                    attention_masks.append(mask)
        else:
            padded_texts = encoded_texts
            attention_masks = [[1] * len(ids) for ids in encoded_texts] if return_attention_mask else None
        
        # Prepare output dictionary
        output = {'input_ids': padded_texts}
        if return_attention_mask:
            output['attention_mask'] = attention_masks
            
        # Convert to tensors if requested
        if return_tensors == 'pt':
            if not TORCH_AVAILABLE:
                raise ImportError("PyTorch is not installed. Install it with 'pip install torch'.")
            
            for key in output:
                output[key] = torch.tensor(output[key])
                
        return output
    
    @staticmethod
    def collate_fn(batch: List[Dict[str, Any]], 
                  pad_token_id: int) -> Dict[str, 'torch.Tensor']:
        """
        Collate function for PyTorch DataLoader.
        
        Args:
            batch: List of dictionaries with 'input_ids' and other fields
            pad_token_id: ID of the padding token
            
        Returns:
            Dictionary with batched tensors
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is not installed. Install it with 'pip install torch'.")
            
        # Get all keys from the first batch element
        keys = batch[0].keys()
        
        result = {}
        for key in keys:
            if key == 'input_ids':
                # Get sequence lengths
                lengths = [len(item[key]) for item in batch]
                max_length = max(lengths)
                
                # Pad sequences and create tensor
                padded = [
                    item[key] + [pad_token_id] * (max_length - len(item[key]))
                    for item in batch
                ]
                result[key] = torch.tensor(padded)
                
                # Add sequence lengths if not present
                if 'lengths' not in keys:
                    result['lengths'] = torch.tensor(lengths)
                    
            elif key == 'attention_mask':
                # Get sequence lengths
                lengths = [len(item['input_ids']) for item in batch]
                max_length = max(lengths)
                
                # Create attention masks
                attention_masks = [
                    [1] * len(item['input_ids']) + [0] * (max_length - len(item['input_ids']))
                    for item in batch
                ]
                result[key] = torch.tensor(attention_masks)
                
            elif isinstance(batch[0][key], torch.Tensor):
                # For other tensor fields, stack them
                result[key] = torch.stack([item[key] for item in batch])
                
            elif isinstance(batch[0][key], (int, float, bool)):
                # For scalar fields, create a tensor
                result[key] = torch.tensor([item[key] for item in batch])
                
            else:
                # For other fields, just collect them as a list
                result[key] = [item[key] for item in batch]
                
        return result


# Helper functions for common text cleaning tasks
def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    html_pattern = re.compile('<.*?>')
    return html_pattern.sub('', text)

def clean_urls(text: str) -> str:
    """Remove URLs from text."""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub('', text)

def clean_emojis(text: str) -> str:
    """Remove emojis from text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+"
    )
    return emoji_pattern.sub('', text)

def clean_multiple_spaces(text: str) -> str:
    """Replace multiple spaces with single space."""
    return re.sub(r'\s+', ' ', text).strip()


# Example usage
def example_usage():
    texts = [
        "Hello world! This is an example sentence for tokenization.",
        "Word2Vec and GloVe are popular word embedding models.",
        "NLP tasks often require preprocessing steps like stemming and lemmatization.",
        "The quick brown fox jumps over the lazy dog.",
    ]
    
    # Basic tokenizer
    tokenizer = Tokenizer(
        lowercase=True,
        remove_punctuation=True,
        remove_stopwords=True,
        language='english'
    )
    
    # Tokenize texts
    tokenized_texts = tokenizer.tokenize_texts(texts)
    print(f"Tokenized texts: {tokenized_texts}")
    
    # Prepare for word embeddings
    processed_texts, vocab = tokenizer.prepare_for_word_embeddings(texts, min_count=1)
    print(f"Vocabulary size: {len(vocab)}")
    print(f"Vocabulary: {vocab}")
    
    # Demonstrate tokenizing with n-grams
    n_gram_tokenizer = Tokenizer(
        lowercase=True,
        remove_punctuation=True,
        keep_n_grams=[2, 3]
    )
    
    tokenized_with_ngrams = n_gram_tokenizer.tokenize_text(texts[0])
    print(f"With n-grams: {tokenized_with_ngrams}")
    
    # Example with special tokens and PyTorch integration
    if TORCH_AVAILABLE:
        advanced_tokenizer = Tokenizer(
            lowercase=True,
            remove_punctuation=True,
            remove_stopwords=True,
            language='english'
        )
        
        texts = [
            "The first example sentence for demonstration.",
            "The second example is a bit longer to show padding."
        ]
        
        # Build vocabulary
        advanced_tokenizer.build_vocab(texts, min_count=1)
        
        # Encode as tensors with padding
        encoded = advanced_tokenizer.batch_encode_as_tensors(
            texts, 
            padding=True,
            return_attention_mask=True
        )
        
        print(f"Input IDs shape: {encoded['input_ids'].shape}")
        print(f"Attention mask shape: {encoded['attention_mask'].shape}")
        
        # Decode back
        decoded = advanced_tokenizer.decode(encoded['input_ids'][0].tolist())
        print(f"Decoded text: {decoded}")
        
        # Example with Hugging Face datasets and PyTorch DataLoaders
        try:
            import datasets
            from torch.utils.data import Dataset, DataLoader
            
            # Load the rotten_tomatoes dataset
            print("Loading Rotten Tomatoes dataset...")
            dataset = datasets.load_dataset("rotten_tomatoes")
            
            # Create a simple dataset class
            class TextClassificationDataset(Dataset):
                def __init__(self, texts, labels, tokenizer, max_length=128):
                    self.texts = texts
                    self.labels = labels
                    self.tokenizer = tokenizer
                    self.max_length = max_length
                
                def __len__(self):
                    return len(self.texts)
                
                def __getitem__(self, idx):
                    text = self.texts[idx]
                    label = self.labels[idx]
                    
                    # Encode text
                    encoding = self.tokenizer.batch_encode_as_tensors(
                        [text], 
                        add_special_tokens=True,
                        padding=True,
                        truncation=True,
                        max_length=self.max_length,
                        return_attention_mask=True,
                        return_tensors=None  # We'll convert to tensors later
                    )
                    
                    # Convert to tensors
                    return {
                        'input_ids': torch.tensor(encoding['input_ids'][0]),
                        'attention_mask': torch.tensor(encoding['attention_mask'][0]),
                        'label': torch.tensor(label)
                    }
            
            # Build vocabulary from training data
            # Get text samples for building vocab
            train_texts = dataset['train']['text'][:1000]  # Using first 1000 samples for demonstration
            
            # Create tokenizer and build vocab
            rt_tokenizer = Tokenizer(
                lowercase=True,
                remove_punctuation=True,
                remove_stopwords=False
            )
            
            rt_tokenizer.build_vocab(train_texts, min_count=2)
            print(f"Built vocabulary of size: {len(rt_tokenizer.token_to_id)}")
            
            # Create PyTorch datasets
            train_dataset = TextClassificationDataset(
                dataset['train']['text'],
                dataset['train']['label'],
                rt_tokenizer
            )
            
            val_dataset = TextClassificationDataset(
                dataset['validation']['text'],
                dataset['validation']['label'],
                rt_tokenizer
            )
            
            # Create DataLoaders
            batch_size = 16
            
            train_loader = DataLoader(
                train_dataset,
                batch_size=batch_size,
                shuffle=True,
                collate_fn=lambda batch: Tokenizer.collate_fn(batch, rt_tokenizer.pad_token_id)
            )
            
            val_loader = DataLoader(
                val_dataset,
                batch_size=batch_size,
                shuffle=False,
                collate_fn=lambda batch: Tokenizer.collate_fn(batch, rt_tokenizer.pad_token_id)
            )
            
            # Show a batch
            print("\nExample batch from DataLoader:")
            for batch in train_loader:
                print(f"Input IDs shape: {batch['input_ids'].shape}")
                print(f"Attention mask shape: {batch['attention_mask'].shape}")
                print(f"Labels shape: {batch['label'].shape}")
                
                # Decode a sample
                sample_idx = 0
                print(f"\nSample text decoded: {rt_tokenizer.decode(batch['input_ids'][sample_idx].tolist(), skip_special_tokens=True)}")
                print(f"Sample label: {batch['label'][sample_idx].item()}")
                break
                
        except ImportError:
            print("Hugging Face datasets library not available. Install with 'pip install datasets'")
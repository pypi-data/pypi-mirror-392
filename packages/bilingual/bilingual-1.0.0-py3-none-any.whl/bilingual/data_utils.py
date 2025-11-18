"""
Dataset utilities for loading, processing, and managing bilingual data.

Handles various dataset formats and provides preprocessing pipelines.
"""

import json
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

try:
    import requests
    from bs4 import BeautifulSoup

    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    requests = None
    BeautifulSoup = None


class BilingualDataset:
    """
    Dataset class for bilingual text data.

    Supports loading from various formats (JSONL, TSV, TXT).
    """

    def __init__(
        self,
        data: Optional[List[Dict[str, Any]]] = None,
        file_path: Optional[str] = None,
    ):
        """
        Initialize dataset.

        Args:
            data: List of data samples
            file_path: Path to load data from
        """
        self.data = data or []

        if file_path:
            self.load(file_path)

    def load(self, file_path: str) -> None:
        """
        Load data from file.

        Args:
            file_path: Path to data file (.jsonl, .json, .tsv, .txt)
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix == ".jsonl":
            self.data = self._load_jsonl(path)
        elif path.suffix == ".json":
            self.data = self._load_json(path)
        elif path.suffix == ".tsv":
            self.data = self._load_tsv(path)
        elif path.suffix == ".txt":
            self.data = self._load_txt(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    def _load_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load JSONL file."""
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        return data

    def _load_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle both list and dict formats
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            return []

    def _load_tsv(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load TSV file."""
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            header = f.readline().strip().split("\t")
            for line in f:
                values = line.strip().split("\t")
                if len(values) == len(header):
                    data.append(dict(zip(header, values)))
        return data

    def _load_txt(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load plain text file (one sample per line)."""
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append({"text": line})
        return data

    def save(self, file_path: str, format: str = "jsonl") -> None:
        """
        Save dataset to file.

        Args:
            file_path: Output file path
            format: Output format ('jsonl', 'json', 'tsv')
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "jsonl":
            with open(path, "w", encoding="utf-8") as f:
                for item in self.data:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

        elif format == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

        elif format == "tsv":
            if not self.data:
                return

            keys = list(self.data[0].keys())
            with open(path, "w", encoding="utf-8") as f:
                f.write("\t".join(keys) + "\n")
                for item in self.data:
                    values = [str(item.get(k, "")) for k in keys]
                    f.write("\t".join(values) + "\n")

        else:
            raise ValueError(f"Unsupported format: {format}")

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        return self.data[idx]

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return iter(self.data)

    def shuffle(self, seed: Optional[int] = None) -> None:
        """Shuffle the dataset in place."""
        if seed is not None:
            random.seed(seed)
        random.shuffle(self.data)

    def split(
        self,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: Optional[int] = None,
    ) -> Tuple["BilingualDataset", "BilingualDataset", "BilingualDataset"]:
        """
        Split dataset into train/val/test sets.

        Args:
            train_ratio: Proportion for training set
            val_ratio: Proportion for validation set
            test_ratio: Proportion for test set
            seed: Random seed for reproducibility

        Returns:
            Tuple of (train_dataset, val_dataset, test_dataset)
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"

        if seed is not None:
            random.seed(seed)

        # Shuffle data
        data_copy = self.data.copy()
        random.shuffle(data_copy)

        # Calculate split indices
        n = len(data_copy)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)

        # Create splits
        train_data = BilingualDataset(data=data_copy[:train_end])
        val_data = BilingualDataset(data=data_copy[train_end:val_end])
        test_data = BilingualDataset(data=data_copy[val_end:])

        return train_data, val_data, test_data

    def filter(self, condition) -> "BilingualDataset":
        """
        Filter dataset based on a condition.

        Args:
            condition: Function that takes a sample and returns bool

        Returns:
            New filtered dataset
        """
        filtered_data = [item for item in self.data if condition(item)]
        return BilingualDataset(data=filtered_data)

    def map(self, transform) -> "BilingualDataset":
        """
        Apply a transformation to all samples.

        Args:
            transform: Function that takes a sample and returns transformed sample

        Returns:
            New transformed dataset
        """
        transformed_data = [transform(item) for item in self.data]
        return BilingualDataset(data=transformed_data)


def load_parallel_corpus(
    src_file: str,
    tgt_file: str,
    src_lang: str = "bn",
    tgt_lang: str = "en",
) -> BilingualDataset:
    """
    Load parallel corpus from separate source and target files.

    Args:
        src_file: Path to source language file
        tgt_file: Path to target language file
        src_lang: Source language code
        tgt_lang: Target language code

    Returns:
        BilingualDataset with parallel sentences
    """
    with open(src_file, "r", encoding="utf-8") as f_src, open(
        tgt_file, "r", encoding="utf-8"
    ) as f_tgt:
        src_lines = [line.strip() for line in f_src if line.strip()]
        tgt_lines = [line.strip() for line in f_tgt if line.strip()]

    if len(src_lines) != len(tgt_lines):
        raise ValueError(
            f"Source and target files have different number of lines: "
            f"{len(src_lines)} vs {len(tgt_lines)}"
        )

    data = [
        {
            "src": src,
            "tgt": tgt,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
        }
        for src, tgt in zip(src_lines, tgt_lines)
    ]

    return BilingualDataset(data=data)


def combine_corpora(*datasets: BilingualDataset) -> BilingualDataset:
    """
    Combine multiple datasets into one.

    Args:
        *datasets: Variable number of BilingualDataset instances

    Returns:
        Combined dataset
    """
    combined_data = []
    for dataset in datasets:
        combined_data.extend(dataset.data)
    return BilingualDataset(data=combined_data)


"""
Enhanced data collection utilities for bilingual corpus.

This module provides advanced web scraping and data collection capabilities
for educational content, news, and other sources.
"""

try:
    from fake_useragent import UserAgent

    FAKE_USERAGENT_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False
    UserAgent = None


class EnhancedDataCollector:
    """
    Enhanced data collector for web scraping and corpus building.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize the data collector.

        Args:
            output_dir: Directory to save collected data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ua = UserAgent() if FAKE_USERAGENT_AVAILABLE else None

        # Headers for requests
        user_agent = (
            self.ua.random
            if self.ua
            else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def scrape_educational_content(self, url: str, limit: Optional[int] = None) -> List[str]:
        """
        Scrape educational content from a URL.

        Args:
            url: Target URL to scrape
            limit: Maximum number of articles to collect

        Returns:
            List of scraped text content
        """
        try:
            print(f"    🌐 Fetching content from: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text_content = []

            # Try different content selectors for educational sites
            content_selectors = [
                "article",
                ".content",
                ".post-content",
                ".entry-content",
                "main",
                ".main-content",
                'div[class*="content"]',
                'div[class*="article"]',
                'div[class*="post"]',
            ]

            content_found = False
            for selector in content_selectors:
                content_divs = soup.select(selector)
                if content_divs:
                    for div in content_divs[: limit or 5]:  # Limit articles
                        text = div.get_text(separator=" ", strip=True)
                        if len(text) > 100:  # Only substantial content
                            text_content.append(text)
                            content_found = True
                            if limit and len(text_content) >= limit:
                                break
                    if content_found:
                        break

            # Fallback: get all paragraph text
            if not content_found:
                paragraphs = soup.find_all("p")
                for p in paragraphs[: limit or 10]:
                    text = p.get_text(strip=True)
                    if len(text) > 50:
                        text_content.append(text)

            # Save to file
            if text_content:
                domain = url.split("//")[1].split("/")[0].replace(".", "_")
                filename = self.output_dir / f"educational_{domain}.txt"

                with open(filename, "a", encoding="utf-8") as f:
                    for content in text_content:
                        f.write(content + "\n\n")
                        f.write("=" * 80 + "\n\n")

                print(f"    💾 Saved {len(text_content)} articles to {filename}")

            return text_content

        except Exception as e:
            print(f"    ❌ Error scraping {url}: {e}")
            return []

    def scrape_news_content(self, url: str, limit: Optional[int] = None) -> List[str]:
        """
        Scrape news content from a URL.

        Args:
            url: Target news URL to scrape
            limit: Maximum number of articles to collect

        Returns:
            List of scraped news articles
        """
        try:
            print(f"    📰 Fetching news from: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            articles = []

            # Try different article selectors for news sites
            article_selectors = [
                "article",
                ".news-item",
                ".post",
                ".entry",
                'div[class*="article"]',
                'div[class*="news"]',
                'div[class*="post"]',
                ".story",
                ".headline",
            ]

            for selector in article_selectors:
                article_divs = soup.select(selector)
                for div in article_divs[: limit or 10]:
                    # Extract title and content
                    title_elem = div.find(["h1", "h2", "h3", ".title", ".headline"])
                    content_elem = div.find(["p", ".content", ".summary", ".excerpt"])

                    title = title_elem.get_text(strip=True) if title_elem else ""
                    content = content_elem.get_text(strip=True) if content_elem else ""

                    if title or (content and len(content) > 100):
                        article_text = f"{title}\n\n{content}" if title else content
                        articles.append(article_text)

                        if limit and len(articles) >= limit:
                            break

                if articles:
                    break

            # Save to file
            if articles:
                domain = url.split("//")[1].split("/")[0].replace(".", "_")
                filename = self.output_dir / f"news_{domain}.txt"

                with open(filename, "a", encoding="utf-8") as f:
                    for article in articles:
                        f.write(article + "\n\n")
                        f.write("=" * 80 + "\n\n")

                print(f"    💾 Saved {len(articles)} articles to {filename}")

            return articles

        except Exception as e:
            print(f"    ❌ Error scraping news from {url}: {e}")
            return []

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize scraped text.

        Args:
            text: Raw scraped text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep Bengali and English
        text = re.sub(r"[^\u0980-\u09FF\u0000-\u007F\s]", "", text)

        # Remove URLs
        text = re.sub(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "",
            text,
        )

        # Remove email addresses
        text = re.sub(r"\S+@\S+", "", text)

        return text.strip()

    def collect_parallel_sentences(self, bn_file: str, en_file: str) -> List[Dict[str, str]]:
        """
        Create parallel corpus from separate Bangla and English files.

        Args:
            bn_file: Path to Bangla text file
            en_file: Path to English text file

        Returns:
            List of parallel sentence pairs
        """
        parallel_data = []

        try:
            with open(bn_file, "r", encoding="utf-8") as f:
                bn_sentences = [line.strip() for line in f if line.strip()]

            with open(en_file, "r", encoding="utf-8") as f:
                en_sentences = [line.strip() for line in f if line.strip()]

            # Simple alignment (take min length and pair sequentially)
            min_len = min(len(bn_sentences), len(en_sentences))

            for i in range(min_len):
                if len(bn_sentences[i]) > 10 and len(en_sentences[i]) > 10:
                    parallel_data.append(
                        {
                            "bn": self.clean_text(bn_sentences[i]),
                            "en": self.clean_text(en_sentences[i]),
                        }
                    )

            # Save parallel corpus
            parallel_file = self.output_dir / "parallel_corpus.jsonl"
            with open(parallel_file, "w", encoding="utf-8") as f:
                for pair in parallel_data:
                    f.write(json.dumps(pair, ensure_ascii=False) + "\n")

            print(f"    🔗 Created {len(parallel_data)} parallel pairs")

        except Exception as e:
            print(f"    ❌ Error creating parallel corpus: {e}")

        return parallel_data

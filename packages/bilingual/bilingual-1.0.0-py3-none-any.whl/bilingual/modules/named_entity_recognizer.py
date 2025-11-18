"""
Named Entity Recognition for Bangla text.

This module provides NER functionality to extract and classify named entities
such as persons, locations, organizations, dates, etc. from Bangla text.
"""

from typing import Dict, List


def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Extract named entities from Bangla text.

    Args:
        text: Input text to analyze

    Returns:
        List of entities with their text, type, and position
    """
    # TODO: Implement NER logic using models like mBERT-NER or custom trained models
    # Entity types: PERSON, LOCATION, ORGANIZATION, DATE, TIME, etc.
    return []


def extract_entities_by_type(text: str, entity_type: str) -> List[str]:
    """
    Extract entities of a specific type from text.

    Args:
        text: Input text to analyze
        entity_type: Type of entity to extract (e.g., 'PERSON', 'LOCATION')

    Returns:
        List of entity texts matching the specified type
    """
    entities = extract_entities(text)
    return [e["text"] for e in entities if e.get("type") == entity_type]


def annotate_entities(text: str) -> str:
    """
    Annotate text with entity tags.

    Args:
        text: Input text to annotate

    Returns:
        Text with inline entity annotations
    """
    # TODO: Implement entity annotation logic
    # Example output: "আমি <PERSON>রবীন্দ্রনাথ</PERSON> <LOCATION>কলকাতায়</LOCATION> থাকি।"
    return text


def get_entity_types() -> List[str]:
    """
    Get list of supported entity types.

    Returns:
        List of entity type names
    """
    return ["PERSON", "LOCATION", "ORGANIZATION", "DATE", "TIME", "MONEY", "PERCENT", "MISC"]

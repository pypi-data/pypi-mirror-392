"""Tests for pysummarize core functions."""

from pylib-summarize import (
    summarize_frequency,
    summarize_sentences,
    extract_keywords,
    summarize_by_ratio,
)


def test_summarize_sentences():
    text = "First sentence. Second sentence. Third sentence."
    result = summarize_sentences(text, 2)
    assert "First sentence" in result
    assert "Second sentence" in result


def test_extract_keywords():
    text = "Python is a great programming language. Python is used for data science."
    keywords = extract_keywords(text, 3)
    assert len(keywords) <= 3
    assert "python" in keywords


def test_summarize_by_ratio():
    text = "First. Second. Third. Fourth. Fifth."
    result = summarize_by_ratio(text, 0.4)
    assert len(result) > 0


"""
Test script for conversion with AI options.
Run with: python tests/test_conversion.py
"""
import sys
import os

# Add app directory to path (same as main.py does)
app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Now import using the same style as main.py
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_conversion():
    """Test basic conversion without AI."""
    from converter import MarkdownConverter, AIOptions

    conv = MarkdownConverter()
    ai_opts = AIOptions(
        api_key='',
        summary_enabled=False,
        chunk_enabled=False,
        extract_images=False
    )
    conv.set_ai_options(ai_opts)

    # Use main.py as test file
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'main.py')
    result = conv.convert_file(test_file, None, overwrite=True)

    print(f"[BASIC] success={result.success}, output={result.output_path}")
    assert result.success, f"Basic conversion failed: {result.error_message}"
    return result

def test_ai_summarization():
    """Test conversion with AI summarization (will fail with invalid key)."""
    from converter import MarkdownConverter, AIOptions

    conv = MarkdownConverter()
    ai_opts = AIOptions(
        api_key='sk-test-invalid-key',  # Invalid key for testing
        base_url='https://api.openai.com/v1',
        model='gpt-4o-mini',
        summary_enabled=True,
        chunk_enabled=False,
        extract_images=False
    )
    conv.set_ai_options(ai_opts)

    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'main.py')
    result = conv.convert_file(test_file, None, overwrite=True)

    print(f"[AI SUMMARY] success={result.success}, error={result.error_message}")
    # Should still succeed even with API error, just no summary added
    assert result.success, f"AI conversion failed: {result.error_message}"
    return result

def test_rag_chunking():
    """Test conversion with RAG chunking."""
    from converter import MarkdownConverter, AIOptions

    conv = MarkdownConverter()
    ai_opts = AIOptions(
        api_key='',
        summary_enabled=False,
        chunk_enabled=True,  # Enable RAG chunking
        extract_images=False
    )
    conv.set_ai_options(ai_opts)

    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'main.py')
    result = conv.convert_file(test_file, None, overwrite=True)

    print(f"[RAG] success={result.success}, output={result.output_path}")
    # Check if JSONL was created
    if result.output_path:
        jsonl_path = result.output_path.replace('.md', '.jsonl')
        print(f"[RAG] jsonl exists: {os.path.exists(jsonl_path)}")
    assert result.success, f"RAG conversion failed: {result.error_message}"
    return result

if __name__ == '__main__':
    print("=" * 50)
    print("Testing conversion with AI options...")
    print("=" * 50)

    print("\n1. Testing basic conversion (no AI)...")
    test_basic_conversion()

    print("\n2. Testing AI summarization (expect API error)...")
    test_ai_summarization()

    print("\n3. Testing RAG chunking...")
    test_rag_chunking()

    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)

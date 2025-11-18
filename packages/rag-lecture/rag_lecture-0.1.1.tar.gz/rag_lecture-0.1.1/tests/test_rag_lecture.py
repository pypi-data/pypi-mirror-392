from rag_lecture import RAGLecture
import os

def test_index_and_query(tmp_path):
    # create a temporary directory for persistence
    temp_dir = tmp_path / "index"
    rag = RAGLecture(persist_dir=str(temp_dir))

    # load a small test folder (should contain sample PDFs)
    test_folder = "tests/test_data"
    rag.index_folder(test_folder, reset=True)

    # basic test: retriever exists
    assert rag.retriever is not None

    # ask something (mock question)
    try:
        rag.ask("Explain backpropagation")
    except Exception as e:
        # Should not throw unless OpenAI API credentials are missing
        assert "No index loaded" not in str(e)

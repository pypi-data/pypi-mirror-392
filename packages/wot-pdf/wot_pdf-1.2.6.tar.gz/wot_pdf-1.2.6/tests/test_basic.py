"""
Basic tests for WOT-PDF functionality
"""

import pytest
from pathlib import Path
from wot_pdf import PDFGenerator, generate_pdf, generate_book


def test_pdf_generator_import():
    """Test that PDFGenerator can be imported"""
    assert PDFGenerator is not None


def test_generate_pdf_import():
    """Test that generate_pdf function can be imported"""
    assert generate_pdf is not None


def test_generate_book_import():
    """Test that generate_book function can be imported"""
    assert generate_book is not None


def test_pdf_generator_initialization():
    """Test that PDFGenerator can be initialized"""
    generator = PDFGenerator()
    assert generator is not None


def test_version():
    """Test that version is available"""
    from wot_pdf import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_templates_available():
    """Test that templates are available"""
    from wot_pdf import TEMPLATES
    assert TEMPLATES is not None
    assert len(TEMPLATES) > 0
    assert 'technical' in TEMPLATES
    assert 'academic' in TEMPLATES


@pytest.mark.integration
def test_simple_pdf_generation(tmp_path):
    """Test basic PDF generation"""
    # Create simple markdown
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Document\\n\\nThis is a test.")
    
    # Generate PDF
    generator = PDFGenerator()
    pdf_file = tmp_path / "test.pdf"
    
    result = generator.generate(str(md_file), str(pdf_file))
    
    # Check result
    assert result is not None
    assert result.get('success', False)
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0


@pytest.mark.integration
def test_book_generation(tmp_path):
    """Test book generation from multiple files"""
    # Create test directory with multiple markdown files
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    (docs_dir / "01_intro.md").write_text("# Introduction\\n\\nFirst chapter.")
    (docs_dir / "02_content.md").write_text("# Content\\n\\nSecond chapter.")
    (docs_dir / "03_conclusion.md").write_text("# Conclusion\\n\\nFinal chapter.")
    
    # Generate book
    pdf_file = tmp_path / "book.pdf"
    
    result = generate_book(
        input_dir=str(docs_dir),
        output_file=str(pdf_file),
        template="technical"
    )
    
    # Check result
    assert result is not None
    assert result.get('success', False)
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

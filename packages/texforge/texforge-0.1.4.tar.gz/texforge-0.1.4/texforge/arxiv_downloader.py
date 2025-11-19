#!/usr/bin/env python3
"""
ArXiv Paper Downloader
Downloads arXiv papers in multiple formats: LaTeX source (default), PDF, or HTML
"""
import re
import tarfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.error


class ArXivDownloader:
    """Download and extract arXiv source files"""

    ARXIV_URL_PATTERNS = [
        r'arxiv\.org/abs/(\d+\.\d+)',
        r'arxiv\.org/pdf/(\d+\.\d+)',
        r'^(\d+\.\d+)$',  # Just the ID
    ]

    def __init__(self, library_dir: Path):
        """Initialize with library directory path"""
        self.library_dir = Path(library_dir)
        self.library_dir.mkdir(parents=True, exist_ok=True)

    def extract_arxiv_id(self, url_or_id: str) -> Optional[str]:
        """Extract arXiv ID from various formats"""
        for pattern in self.ARXIV_URL_PATTERNS:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        return None

    def download_source(self, url_or_id: str, custom_name: Optional[str] = None, format: str = "latex") -> Optional[Path]:
        """
        Download arXiv paper in specified format

        Args:
            url_or_id: ArXiv URL or ID (e.g., "2301.12345" or "https://arxiv.org/abs/2301.12345")
            custom_name: Optional custom folder name (default: arxiv_XXXXX)
            format: Download format - "latex" (default), "pdf", or "html"

        Returns:
            Path to downloaded file/folder or None if failed
        """
        arxiv_id = self.extract_arxiv_id(url_or_id)
        if not arxiv_id:
            print(f"❌ Could not extract arXiv ID from: {url_or_id}")
            return None

        if format == "latex":
            return self._download_latex_source(arxiv_id, custom_name)
        elif format == "pdf":
            return self._download_pdf(arxiv_id, custom_name)
        elif format == "html":
            return self._download_html(arxiv_id, custom_name)
        else:
            raise ValueError(f"Invalid format: {format}. Must be 'latex', 'pdf', or 'html'")

    def _download_latex_source(self, arxiv_id: str, custom_name: Optional[str] = None) -> Optional[Path]:
        """
        Download arXiv LaTeX source and extract to library/

        Args:
            arxiv_id: ArXiv ID (e.g., "2301.12345")
            custom_name: Optional custom folder name (default: arxiv_XXXXX)

        Returns:
            Path to extracted folder or None if failed
        """
        print(f"📥 Downloading arXiv LaTeX source: {arxiv_id}")

        # Determine folder name
        folder_name = custom_name if custom_name else f"arxiv_{arxiv_id.replace('.', '_')}"
        extract_path = self.library_dir / folder_name

        # Check if already exists
        if extract_path.exists():
            print(f"⚠️  Folder already exists: {extract_path}")
            response = input("Overwrite? (y/n): ").lower().strip()
            if response != 'y':
                print("Skipping download.")
                return extract_path
            shutil.rmtree(extract_path)

        # Download source tarball
        source_url = f"https://arxiv.org/e-print/{arxiv_id}"

        try:
            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
                print(f"  Fetching {source_url}...")
                urllib.request.urlretrieve(source_url, tmp_file.name)
                tmp_path = Path(tmp_file.name)

            # Extract tarball
            print(f"  Extracting to {extract_path}...")
            extract_path.mkdir(parents=True, exist_ok=True)

            try:
                with tarfile.open(tmp_path, 'r:gz') as tar:
                    tar.extractall(path=extract_path)
            except tarfile.ReadError:
                # Some arXiv sources are just .tar without gz
                with tarfile.open(tmp_path, 'r:') as tar:
                    tar.extractall(path=extract_path)

            # Clean up temp file
            tmp_path.unlink()

            # List extracted files
            tex_files = list(extract_path.glob("*.tex"))
            bib_files = list(extract_path.glob("*.bib"))
            bbl_files = list(extract_path.glob("*.bbl"))

            print(f"✅ Downloaded to: {extract_path}")
            print(f"   📄 Found: {len(tex_files)} .tex, {len(bib_files)} .bib, {len(bbl_files)} .bbl files")

            return extract_path

        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise RuntimeError(f"Access denied. Paper {arxiv_id} may not have LaTeX source available.")
            else:
                raise RuntimeError(f"HTTP Error {e.code}: {e.reason}")
        except Exception as e:
            raise RuntimeError(f"Error downloading LaTeX source for {arxiv_id}: {e}")

    def _download_pdf(self, arxiv_id: str, custom_name: Optional[str] = None) -> Optional[Path]:
        """
        Download arXiv paper as PDF

        Args:
            arxiv_id: ArXiv ID (e.g., "2301.12345")
            custom_name: Optional custom filename (default: arxiv_XXXXX.pdf)

        Returns:
            Path to downloaded PDF file or None if failed
        """
        print(f"📥 Downloading arXiv PDF: {arxiv_id}")

        # Determine filename
        filename = custom_name if custom_name else f"arxiv_{arxiv_id.replace('.', '_')}.pdf"
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        pdf_path = self.library_dir / filename

        # Check if already exists
        if pdf_path.exists():
            print(f"⚠️  File already exists: {pdf_path}")
            response = input("Overwrite? (y/n): ").lower().strip()
            if response != 'y':
                print("Skipping download.")
                return pdf_path

        # Download PDF
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        try:
            print(f"  Fetching {pdf_url}...")
            urllib.request.urlretrieve(pdf_url, pdf_path)

            # Verify the file is actually a PDF
            with open(pdf_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    pdf_path.unlink()
                    raise RuntimeError(f"Downloaded file is not a valid PDF for arXiv ID {arxiv_id}")

            print(f"✅ Downloaded PDF to: {pdf_path}")
            return pdf_path

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise RuntimeError(f"PDF not found for arXiv ID {arxiv_id}")
            else:
                raise RuntimeError(f"HTTP Error {e.code}: {e.reason}")
        except Exception as e:
            if pdf_path.exists():
                pdf_path.unlink()
            raise RuntimeError(f"Error downloading PDF for {arxiv_id}: {e}")

    def _download_html(self, arxiv_id: str, custom_name: Optional[str] = None) -> Optional[Path]:
        """
        Download arXiv paper as HTML from ar5iv.labs.arxiv.org

        Args:
            arxiv_id: ArXiv ID (e.g., "2301.12345")
            custom_name: Optional custom filename (default: arxiv_XXXXX.html)

        Returns:
            Path to downloaded HTML file or None if failed
        """
        print(f"📥 Downloading arXiv HTML: {arxiv_id}")

        # Determine filename
        filename = custom_name if custom_name else f"arxiv_{arxiv_id.replace('.', '_')}.html"
        if not filename.endswith('.html'):
            filename += '.html'
        html_path = self.library_dir / filename

        # Check if already exists
        if html_path.exists():
            print(f"⚠️  File already exists: {html_path}")
            response = input("Overwrite? (y/n): ").lower().strip()
            if response != 'y':
                print("Skipping download.")
                return html_path

        # Download HTML from ar5iv
        html_url = f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"

        try:
            print(f"  Fetching {html_url}...")
            urllib.request.urlretrieve(html_url, html_path)

            # Verify the file contains HTML
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # Read first 1000 chars
                if not ('<html' in content.lower() or '<!doctype html' in content.lower()):
                    html_path.unlink()
                    raise RuntimeError(f"Downloaded file is not valid HTML for arXiv ID {arxiv_id}")

            print(f"✅ Downloaded HTML to: {html_path}")
            return html_path

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise RuntimeError(f"HTML version not available for arXiv ID {arxiv_id} on ar5iv.labs.arxiv.org")
            else:
                raise RuntimeError(f"HTTP Error {e.code}: {e.reason}")
        except Exception as e:
            if html_path.exists():
                html_path.unlink()
            raise RuntimeError(f"Error downloading HTML for {arxiv_id}: {e}")

    def list_downloaded(self) -> list[Path]:
        """List all downloaded arXiv sources in library/"""
        arxiv_folders = [
            d for d in self.library_dir.iterdir()
            if d.is_dir() and (d.name.startswith('arxiv_') or
                             any(d.glob('*.tex')))  # Any folder with .tex files
        ]
        return sorted(arxiv_folders)

    def find_main_tex(self, arxiv_folder: Path) -> Optional[Path]:
        """Find the main .tex file in an arXiv folder"""
        tex_files = list(arxiv_folder.glob("*.tex"))

        if not tex_files:
            return None

        # Look for common main file names
        main_names = ['main.tex', 'paper.tex', 'manuscript.tex', 'article.tex']
        for name in main_names:
            candidate = arxiv_folder / name
            if candidate.exists():
                return candidate

        # Look for \documentclass in files
        for tex_file in tex_files:
            try:
                content = tex_file.read_text(errors='ignore')
                if r'\documentclass' in content and r'\begin{document}' in content:
                    return tex_file
            except Exception:
                continue

        # Default to first .tex file
        return tex_files[0] if tex_files else None


def main():
    """CLI for arXiv downloader"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download arXiv papers in various formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download LaTeX source (default)
  texforge arxiv-download 2301.12345

  # Download PDF
  texforge arxiv-download 2301.12345 --format pdf

  # Download HTML version
  texforge arxiv-download 2301.12345 --format html

  # Download by URL
  texforge arxiv-download https://arxiv.org/abs/2301.12345

  # Download with custom name
  texforge arxiv-download 2301.12345 --name quantum_ml_paper

  # List downloaded sources
  texforge arxiv-download --list
        """
    )

    parser.add_argument(
        "arxiv_id",
        nargs='?',
        help="ArXiv ID or URL (e.g., '2301.12345' or 'https://arxiv.org/abs/2301.12345')"
    )
    parser.add_argument(
        "--library",
        type=Path,
        default=Path.cwd() / "library",
        help="Library directory path (default: ./library)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["latex", "pdf", "html"],
        default="latex",
        help="Download format: 'latex' (source code, default), 'pdf', or 'html'"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Custom folder/file name for downloaded content"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all downloaded arXiv sources"
    )

    args = parser.parse_args()

    downloader = ArXivDownloader(args.library)

    if args.list:
        downloaded = downloader.list_downloaded()
        if not downloaded:
            print("No arXiv sources found in library/")
        else:
            print(f"\n📚 Downloaded arXiv sources in {args.library}:\n")
            for folder in downloaded:
                tex_count = len(list(folder.glob("*.tex")))
                bib_count = len(list(folder.glob("*.bib")))
                bbl_count = len(list(folder.glob("*.bbl")))
                print(f"  • {folder.name}/")
                print(f"    {tex_count} .tex, {bib_count} .bib, {bbl_count} .bbl files")
        return 0

    if not args.arxiv_id:
        parser.print_help()
        return 1

    try:
        result = downloader.download_source(args.arxiv_id, args.name, format=args.format)

        if result:
            if args.format == "latex":
                print(f"\n💡 Tip: Run 'texforge brainstorm' to use this reference in your brainstorming session")
            return 0
        else:
            return 1
    except RuntimeError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

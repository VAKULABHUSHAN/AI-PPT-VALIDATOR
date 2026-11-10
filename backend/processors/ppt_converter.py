import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

def find_libreoffice_executable() -> Optional[str]:
    """Search for LibreOffice executable in PATH and standard Windows directories."""
    # 1. Check PATH
    cmd = shutil.which("soffice") or shutil.which("soffice.exe")
    if cmd:
        return cmd
        
    # 2. Check standard Windows installation paths
    common_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\LibreOffice\program\soffice.exe")
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p
            
    return None

def is_powerpoint_com_available() -> bool:
    """Check if Microsoft PowerPoint COM automation is available on Windows."""
    try:
        import comtypes.client
        return True
    except ImportError:
        return False

def get_conversion_diagnostics() -> Dict[str, Any]:
    """Return status of available presentation-to-PDF conversion engines."""
    lo_path = find_libreoffice_executable()
    has_ppt_com = is_powerpoint_com_available()
    
    return {
        "libreoffice_installed": bool(lo_path),
        "libreoffice_path": lo_path,
        "libreoffice_install_instructions": (
            "LibreOffice is not currently installed. To install LibreOffice on Windows:\n"
            "  1. Run in PowerShell: winget install TheDocumentFoundation.LibreOffice\n"
            "  2. Or download directly from: https://www.libreoffice.org/download/download/"
        ) if not lo_path else "LibreOffice is installed and ready.",
        "powerpoint_com_available": has_ppt_com,
        "recommended_engine": "libreoffice" if lo_path else ("powerpoint_com" if has_ppt_com else "native_python_renderer")
    }

def convert_presentation_to_pdf(input_path: Path, output_dir: Path) -> Optional[Path]:
    """
    Convert a PPT or PPTX file to PDF.
    Order of preference:
      1. LibreOffice headless (cross-platform, zero GUI dependency)
      2. Microsoft PowerPoint COM (native Windows Office)
      3. Returns None if neither is available, allowing graceful fallback to python-pptx extraction
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_output_path = output_dir / f"{input_path.stem}.pdf"
    
    # 1. Try LibreOffice headless
    lo_exe = find_libreoffice_executable()
    if lo_exe:
        try:
            logger.info(f"Converting {input_path.name} to PDF using LibreOffice headless...")
            cmd = [
                lo_exe,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(output_dir),
                str(input_path)
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            if result.returncode == 0 and pdf_output_path.exists():
                logger.info(f"LibreOffice successfully converted {input_path.name} to PDF ({os.path.getsize(pdf_output_path)} bytes).")
                return pdf_output_path
            else:
                logger.warning(f"LibreOffice conversion failed with code {result.returncode}: {result.stderr.decode('utf-8', errors='ignore')}")
        except Exception as e:
            logger.error(f"LibreOffice conversion exception: {e}")

    # 2. Try PowerPoint COM automation (Windows)
    if is_powerpoint_com_available():
        try:
            import comtypes.client
            logger.info(f"Converting {input_path.name} to PDF using PowerPoint COM automation...")
            abs_in = os.path.abspath(str(input_path))
            abs_out = os.path.abspath(str(pdf_output_path))
            
            ppt_app = comtypes.client.CreateObject("PowerPoint.Application")
            # Open presentation read-only, without window
            pres = ppt_app.Presentations.Open(abs_in, True, False, False)
            # 32 is ppSaveAsPDF
            pres.SaveAs(abs_out, 32)
            pres.Close()
            ppt_app.Quit()
            
            if os.path.exists(abs_out) and os.path.getsize(abs_out) > 0:
                logger.info(f"PowerPoint COM successfully converted {input_path.name} to PDF ({os.path.getsize(abs_out)} bytes).")
                return pdf_output_path
        except Exception as e:
            logger.error(f"PowerPoint COM conversion exception: {e}")

    logger.info(f"Direct PPT-to-PDF conversion not available; using native python-pptx slide processing.")
    return None


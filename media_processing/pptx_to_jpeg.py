import subprocess
from pathlib import Path
import os
from pdf2image import convert_from_path

reports_dir = Path(__file__).resolve().parent.parent / 'reports'

for report_folder in reports_dir.iterdir():
    if report_folder.is_dir():        
        for file_path in report_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == '.pptx':
                os.chdir(report_folder)
                subprocess.run(
                    [
                        "/usr/bin/lowriter",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        str(file_path.resolve())
                    ],
                    check=True
                )
                no_suffix_path = file_path.with_suffix('')
                no_suffix_path.mkdir(parents=True, exist_ok=True)
                file_path_pdf = file_path.with_suffix('.pdf')
                
                os.chdir(no_suffix_path)
                images = convert_from_path(file_path_pdf)
                
                for i in range(len(images)):
                    images[i].save(file_path.stem + str(i) +'.jpeg', 'JPEG')
                file_path.unlink()
                file_path_pdf.unlink()

"""Convert research PDFs using the existing local Marker environment.

Adapted from why-wiki's preprocess-pdf/convert_pdf.py API pattern:
ConfigParser -> PdfConverter -> save_output directly in a chosen directory.
Load models once for a batch. Preserve PDF bytes and keep conversion separate
from authored knowledge notes. No LLM service is enabled.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, nargs="+")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--page-range", help="Marker zero-based inclusive range, e.g. 0-5")
    parser.add_argument("--batch-size", type=int, default=1,
                        help="Inference batch size; default 1 fits modest GPUs")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")

    from marker.config.parser import ConfigParser
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import save_output

    config = {"output_format": "markdown", "paginate_output": True, "use_llm": False}
    for key in ("layout_batch_size", "detection_batch_size", "ocr_error_batch_size",
                "recognition_batch_size", "equation_batch_size", "table_rec_batch_size"):
        config[key] = args.batch_size
    if args.page_range:
        config["page_range"] = args.page_range
    parsed = ConfigParser(config)
    converter = PdfConverter(
        config=parsed.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=parsed.get_processors(),
        renderer=parsed.get_renderer(),
        llm_service=parsed.get_llm_service(),
    )
    for pdf in args.pdf:
        pdf = pdf.resolve(strict=True)
        checksum = sha256(pdf.read_bytes()).hexdigest()
        output = args.output_root.resolve() / pdf.stem
        output.mkdir(parents=True, exist_ok=True)
        print(f"Converting {pdf.name} -> {output}", flush=True)
        rendered = converter(str(pdf))
        save_output(rendered, str(output), pdf.stem)
        if sha256(pdf.read_bytes()).hexdigest() != checksum:
            raise RuntimeError(f"Original PDF changed: {pdf}")
        import importlib.metadata
        record = {
            "pdf": pdf.name, "pdf_sha256": checksum,
            "marker_version": importlib.metadata.version("marker-pdf"),
            "page_range": args.page_range or "all", "paginate_output": True,
            "batch_size": args.batch_size,
            "use_llm": False, "human_source_verification": "pending",
        }
        (output / "conversion.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"Converted and original checksum preserved: {pdf.name}", flush=True)


if __name__ == "__main__":
    main()

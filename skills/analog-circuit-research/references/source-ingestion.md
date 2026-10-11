# Source ingestion and full-text verification

Use for organizing article series and PDF-assisted research. A local question about one paper does not require a complete source library.

## Three artifact types

- Original sources: preserve original PDF bytes and record source URL, retrieval date, DOI, filename, and SHA256. Bibliographic details may first come from a webpage, then be checked against original pages. Website labels, PDF filenames, and DOI years alone do not determine publication issues.
- Conversion outputs: text, Marker Markdown, extracted images, metadata, and page previews are research aids and belong separately from formal notes. Conversion records include input checksum, tool version, page range, and whether an LLM was used. Do not mark a failed conversion successful.
- Research notes: reorganize material around knowledge questions and derive mechanisms and tradeoffs in your own words. State which conclusions come from the source and which are independent extensions. Extensions may go beyond the series, but new external evidence must remain traceable.

In this project, keep original sources and conversions in ignored `reference/`, verifiable source manifests and checking records in `sources/`, and technical notes in the root. Required citations must not rely solely on untracked local files.

## Conversion and original-page checks

- Reuse an installed Marker environment when available. Its API may follow `ConfigParser → PdfConverter(create_model_dict()) → save_output`. Load models once for batch processing and explicitly select output directories. Marker is not a required research dependency; continue reading original PDFs if conversion is unavailable.
- Marker page ranges are zero-based and inclusive; cited PDF pages are usually one-based. Record printed magazine page numbers separately. Do not mix these three conventions.
- Multiple columns, continuation pages, and shared layouts may contain other articles. Preserve actual PDF page counts and discontinuous printed page numbers; include only the target article in organized text. Leave uncertain page numbers unverified instead of inventing them from webpage spans.
- Check key equations against original pages for subscripts, superscripts, numerators, denominators, signs, and variable definitions. Check circuit diagrams for terminal connections, device types, nodes, and phases. Record pages, figures, or equations for formal notes.
- Converters may leave equations as images, omit numbering, reorder reading flow, or reconstruct mathematics incorrectly. Recheck original images even after successful conversion. Converted Markdown is not evidence of correctness.
- For suspected source errors, confirm the original page first, then check independently using dimensions, state equations, or limiting cases. Record "source expression" and "this note's derivation" separately; do not silently alter original sources.

## Progress through an article series

Track retrieval, conversion, full-text reading, original diagram/equation checking, note preparation, and verification method separately. A topic note may be supported by multiple papers; one PDF need not correspond to one note.

Reassess previous checking status when source checksums change. Distinguish completed topics from materials awaiting research at delivery, and continue to label analytical calculations, transistor-level simulations, and measurements separately.
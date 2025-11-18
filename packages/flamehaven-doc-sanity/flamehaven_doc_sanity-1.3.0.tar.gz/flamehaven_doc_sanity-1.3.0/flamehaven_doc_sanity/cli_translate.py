"""Translation command for CLI - to be integrated into main CLI."""

from pathlib import Path

import click


def add_translate_command(main_group):
    """Add translate command to main CLI group."""

    @main_group.command()
    @click.argument("path", type=click.Path(exists=True))
    @click.option(
        "--source-lang",
        type=click.Choice(["ko", "ja", "zh", "es", "fr", "de", "ru", "auto"]),
        default="auto",
        help="Source language (auto-detect if not specified)",
    )
    @click.option(
        "--target-lang", default="en", help="Target language (default: English)"
    )
    @click.option(
        "--mode",
        type=click.Choice(["rule_based", "ai", "hybrid"]),
        default="rule_based",
        help="Translation mode (ai requires API key)",
    )
    @click.option(
        "--recursive/--no-recursive",
        default=False,
        help="Process directory recursively",
    )
    @click.option(
        "--in-place/--preview",
        default=False,
        help="Apply translations in-place or preview only",
    )
    @click.option(
        "--quality-threshold",
        type=float,
        default=0.85,
        help="Minimum quality threshold (0.0-1.0) for accepting translations",
    )
    def translate(
        path, source_lang, target_lang, mode, recursive, in_place, quality_threshold
    ):
        """Translate code comments and documentation to English.

        \b
        🌍 I18n Translation with MetaCognition (v1.3.0)

        Automatically translates:
        - Inline comments (# comments)
        - Docstrings (function, class, module)
        - README and documentation files

        \b
        With meta-cognitive quality validation:
        - Self-evaluates translation quality
        - Ensures terminology consistency
        - Preserves technical terms
        - Context-aware translation

        \b
        Examples:
            doc-sanity translate my_code.py
            doc-sanity translate src/ --recursive --in-place
            doc-sanity translate README_KR.md --source-lang ko
        """
        from flamehaven_doc_sanity.i18n import (
            CodeCommentParser,
            ConsistencyChecker,
            ContextAnalyzer,
            LanguageDetector,
            TranslationEngine,
            TranslationQualityOracle,
        )

        path_obj = Path(path)

        click.echo(f"\n[I18n Translation System] Starting translation...")
        click.echo(f"Path: {path}")
        click.echo(f"Mode: {mode}")
        click.echo(f"Quality Threshold: {quality_threshold:.2f}\n")

        # Initialize components
        detector = LanguageDetector()
        parser = CodeCommentParser()
        translator = TranslationEngine(mode=mode)
        oracle = TranslationQualityOracle(strict_threshold=quality_threshold)
        consistency = ConsistencyChecker()
        context_analyzer = ContextAnalyzer()

        stats = {
            "files_processed": 0,
            "comments_translated": 0,
            "docstrings_translated": 0,
            "total_nodes": 0,
            "quality_passed": 0,
            "quality_failed": 0,
        }

        # Process file or directory
        if path_obj.is_file():
            files_to_process = [path_obj]
        else:
            if recursive:
                files_to_process = list(path_obj.rglob("*.py"))
            else:
                files_to_process = list(path_obj.glob("*.py"))

        for file_path in files_to_process:
            click.echo(f"\n📄 Processing: {file_path}")

            try:
                # Parse file
                parsed = parser.parse_file(str(file_path))

                if parsed.total_nodes() == 0:
                    click.echo("  ℹ  No translatable content found")
                    continue

                stats["files_processed"] += 1
                stats["total_nodes"] += parsed.total_nodes()

                click.echo(
                    f"  Found {len(parsed.comments)} comments, {len(parsed.docstrings)} docstrings"
                )

                # Translate all nodes
                for node in parsed.get_all_translatable():
                    # Detect language if auto
                    if source_lang == "auto":
                        detection = detector.detect(
                            node.content, context=node.node_type
                        )
                        detected_lang = detection.language
                        confidence = detection.confidence

                        if confidence < 0.5:
                            click.echo(
                                f"  ⚠  Low confidence ({confidence:.2f}) for: {node.content[:50]}..."
                            )
                            continue

                        if detected_lang == "en":
                            # Already English, skip
                            continue
                    else:
                        detected_lang = source_lang

                    # Analyze context
                    context_info = context_analyzer.analyze_context(
                        node.content, node.node_type
                    )

                    # Translate
                    translation = translator.translate(
                        node.content,
                        source_lang=detected_lang,
                        target_lang=target_lang,
                        context=context_info["recommended_approach"],
                    )

                    # Quality validation with MetaCognition
                    assessment = oracle.evaluate(
                        node.content,
                        translation.translated,
                        detected_lang,
                        translation.preserved_terms,
                    )

                    # Check consistency
                    is_consistent, violations = consistency.check_consistency(
                        node.content, translation.translated
                    )

                    if not is_consistent:
                        click.echo(f"  ⚠  Consistency violations:")
                        for violation in violations:
                            click.echo(f"      - {violation}")

                    # Display result
                    omega = assessment.omega_score
                    status = "✓" if omega >= quality_threshold else "✗"

                    click.echo(
                        f"  {status} [{omega:.2f}] {node.node_type} (line {node.line_number})"
                    )

                    if omega >= quality_threshold:
                        stats["quality_passed"] += 1

                        # Register for consistency tracking
                        consistency.register_translation(
                            node.content, translation.translated
                        )

                        # Apply translation if in-place
                        if in_place:
                            node.translated = translation.translated

                            if node.node_type == "inline_comment":
                                stats["comments_translated"] += 1
                            else:
                                stats["docstrings_translated"] += 1
                    else:
                        stats["quality_failed"] += 1

                        click.echo(f"      Issues: {', '.join(assessment.issues)}")
                        for rec in assessment.recommendations:
                            click.echo(f"      💡 {rec}")

                # Write back if in-place mode
                if in_place and any(
                    n.translated for n in parsed.get_all_translatable()
                ):
                    reconstructed = parser.reconstruct_file(parsed)
                    file_path.write_text(reconstructed, encoding=parsed.encoding)
                    click.echo(f"  ✓ File updated")
                elif not in_place:
                    click.echo(f"  ℹ  Preview mode - no changes written")

            except Exception as e:
                click.echo(f"  ✗ Error: {e}", err=True)

        # Summary
        click.echo(f"\n{'='*60}")
        click.echo("[TRANSLATION SUMMARY]")
        click.echo(f"{'='*60}")
        click.echo(f"Files processed: {stats['files_processed']}")
        click.echo(f"Total nodes: {stats['total_nodes']}")
        click.echo(f"Comments translated: {stats['comments_translated']}")
        click.echo(f"Docstrings translated: {stats['docstrings_translated']}")
        click.echo(f"Quality passed: {stats['quality_passed']}/{stats['total_nodes']}")
        click.echo(f"Quality failed: {stats['quality_failed']}/{stats['total_nodes']}")
        click.echo(f"Consistency score: {consistency.get_consistency_score():.2f}")
        click.echo(f"{'='*60}\n")

        if stats["quality_failed"] > 0:
            click.echo("⚠  Some translations did not meet quality threshold.")
            click.echo("   Consider reviewing manually or adjusting threshold.")

    return translate

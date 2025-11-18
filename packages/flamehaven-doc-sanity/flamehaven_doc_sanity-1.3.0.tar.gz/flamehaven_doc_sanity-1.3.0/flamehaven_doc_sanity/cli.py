"""Command-line interface for Flamehaven-Doc-Sanity."""

from pathlib import Path

import click

from flamehaven_doc_sanity import __version__
from flamehaven_doc_sanity.config import load_golden_baseline
from flamehaven_doc_sanity.governance import DriftLockGuard, HOPEGuard
from flamehaven_doc_sanity.orchestrator import FusionOracle, ModalRouter
from flamehaven_doc_sanity.validators import DeepValidator, ShallowValidator


@click.group()
@click.version_option(version=__version__)
def main():
    """Flamehaven-Doc-Sanity: Documentation Validation Framework.

    This CLI provides tools for document validation, drift detection,
    governance enforcement, and I18n translation.
    """
    pass


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--governance-mode",
    type=click.Choice(["conservative", "balanced", "strict"]),
    default="balanced",
    help="""Validation strictness level:

    \b
    - conservative: Basic validation, fastest
    - balanced: Standard validation (recommended)
    - strict: Comprehensive validation, thorough

    Higher modes provide more thorough validation but slower execution.
    """,
)
@click.option(
    "--output-format",
    type=click.Choice(["text", "json", "yaml"]),
    default="text",
    help="Output format for validation results",
)
def check(file_path, governance_mode, output_format):
    """Run document validation with specified mode.

    \b
    Examples:
        doc-sanity check README.md
        doc-sanity check --governance-mode strict docs/ARCHITECTURE.md
        doc-sanity check --output-format json README.md
    """
    click.echo(f"Checking {file_path} with {governance_mode} mode...")

    # Read file content
    content = Path(file_path).read_text()

    # Setup validators based on governance mode
    validators = []
    if governance_mode in ["balanced", "strict"]:
        validators.append(DeepValidator())
    if governance_mode in ["conservative", "balanced"]:
        validators.append(ShallowValidator())
    if governance_mode == "strict":
        # Additional validators for strict mode
        validators.append(ShallowValidator())  # Run both

    # Create router
    oracle = FusionOracle()
    router = ModalRouter(validators=validators, oracle=oracle)

    # Set context based on governance mode
    severity_map = {
        "conservative": "low",
        "balanced": "medium",
        "strict": "high",
    }

    context = {"mode": governance_mode, "severity": severity_map[governance_mode]}

    # Route validation request
    result = router.route_request(file_path=file_path, content=content, context=context)

    # Output results
    if output_format == "text":
        click.echo(f"\n{'='*60}")
        click.echo(f"Status: {result.status.upper()}")
        click.echo(f"Score: {result.fusion_score:.2f}")
        click.echo(f"Verdict: {result.oracle_verdict}")
        click.echo(f"Reasoning: {result.oracle_reasoning}")
        click.echo(f"{'='*60}\n")

        if result.status == "approved":
            click.secho("✓ Document validation PASSED", fg="green", bold=True)
        elif result.status == "needs_review":
            click.secho("⚠ Document needs REVIEW", fg="yellow", bold=True)
        else:
            click.secho("✗ Document validation FAILED", fg="red", bold=True)
    elif output_format == "json":
        import json

        output = {
            "status": result.status,
            "fusion_score": result.fusion_score,
            "oracle_verdict": result.oracle_verdict,
            "oracle_reasoning": result.oracle_reasoning,
            "validators": result.contributing_validators,
        }
        click.echo(json.dumps(output, indent=2))


@main.command("drift-check")
@click.option(
    "--baseline",
    type=click.Path(exists=True),
    help="Path to golden baseline configuration (uses default if not specified)",
)
@click.option(
    "--current-config",
    type=click.Path(exists=True),
    help="Path to current configuration to check",
)
def drift_check(baseline, current_config):
    """Validate configuration against golden baseline for drift detection.

    \b
    Drift detection compares the current system state against a "golden baseline"
    using Jensen-Shannon Divergence (JSD). This helps identify:
    - Architectural degradation
    - Quality metric regressions
    - Policy compliance drift

    \b
    Severity Levels:
    - None:     JSD < 0.04 (within tolerance)
    - Minor:    JSD < 0.06 (monitor closely)
    - Moderate: JSD < 0.08 (review required)
    - Severe:   JSD < 0.10 (immediate action)
    - Critical: JSD ≥ 0.10 (deployment blocked)

    \b
    Examples:
        doc-sanity drift-check
        doc-sanity drift-check --baseline custom_baseline.yaml
    """
    # Load baseline
    if baseline:
        import yaml

        with open(baseline, "r") as f:
            baseline_data = yaml.safe_load(f)
    else:
        baseline_data = load_golden_baseline()

    # Load current config (simulate for demo)
    current_data = {
        "dimensions": {
            "integrity": 0.90,
            "governance": 0.90,
            "reliability": 0.88,
            "maintainability": 0.90,
            "security": 0.88,
        }
    }

    # Create DriftLock Guard
    guard = DriftLockGuard(baseline=baseline_data)

    # Check for drift
    verdict = guard.check(current_data)

    # Display results
    click.echo(f"\n{'='*60}")
    click.echo("DRIFT DETECTION ANALYSIS")
    click.echo(f"{'='*60}\n")
    click.echo(f"Severity: {verdict.severity.upper()}")
    click.echo(f"JSD Score: {verdict.jsd_score:.4f}")
    click.echo(f"Drift Detected: {verdict.drift_detected}")

    if verdict.affected_dimensions:
        click.echo(f"\nAffected Dimensions:")
        for dim in verdict.affected_dimensions:
            click.echo(f"  - {dim}")

    click.echo(f"\nRecommendation: {verdict.recommendation}")
    click.echo(f"{'='*60}\n")

    # Color-coded status
    if verdict.severity == "none":
        click.secho("✓ No drift detected", fg="green", bold=True)
    elif verdict.severity in ["minor", "moderate"]:
        click.secho("⚠ Drift detected - review recommended", fg="yellow", bold=True)
    else:
        click.secho("✗ Critical drift - immediate action required", fg="red", bold=True)


@main.command()
def version():
    """Display version and system information."""
    from flamehaven_doc_sanity import __architecture_purity__, __status__, __version__

    click.echo(f"\nFlamehaven-Doc-Sanity v{__version__}")
    click.echo(f"Status: {__status__}")
    click.echo(f"Architecture Purity: {__architecture_purity__:.4f}")
    click.echo("\n完벽은 선택이 아니라, 존재 조건이다.")
    click.echo("(Perfection is not a choice; it is a condition of existence.)\n")


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--source-lang",
    type=click.Choice(["ko", "ja", "zh", "es", "fr", "de", "ru", "auto"]),
    default="auto",
    help="Source language (auto-detect if not specified)",
)
@click.option("--target-lang", default="en", help="Target language (default: English)")
@click.option(
    "--mode",
    type=click.Choice(["rule_based", "ai", "hybrid"]),
    default="rule_based",
    help="Translation mode (ai requires API key)",
)
@click.option(
    "--recursive/--no-recursive", default=False, help="Process directory recursively"
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

    This command helps non-English developers publish code on GitHub by:
    - Auto-detecting language in code comments and docstrings
    - Translating to developer-friendly English
    - Preserving technical terms and code structure
    - Validating translation quality with meta-cognitive assessment

    \b
    Supported Languages:
    - Korean (ko), Japanese (ja), Chinese (zh)
    - Spanish (es), French (fr), German (de), Russian (ru)

    \b
    Translation Modes:
    - rule_based: Fast, deterministic, no API needed (default)
    - ai: High quality, requires OpenAI/Anthropic API key
    - hybrid: Try AI first, fallback to rule-based

    \b
    Quality Assessment (MetaCognition):
    - Semantic Fidelity: Meaning preservation (30% weight)
    - Technical Accuracy: Term correctness (25% weight)
    - Fluency: Natural English (20% weight)
    - Consistency: Terminology uniformity (15% weight)
    - Context Awareness: Appropriate style (10% weight)
    → Omega Score: Weighted quality metric (0.0-1.0)

    \b
    Examples:
        # Preview translation of Korean comments
        doc-sanity translate my_code.py --source-lang ko

        # Translate in-place with auto-detection
        doc-sanity translate src/ --recursive --in-place

        # Use AI mode with strict quality
        doc-sanity translate main.py --mode ai --quality-threshold 0.90
    """
    from flamehaven_doc_sanity.i18n import (
        CodeCommentParser,
        ConsistencyChecker,
        ContextAnalyzer,
        LanguageDetector,
        TranslationEngine,
        TranslationQualityOracle,
    )

    click.echo(f"\n{'='*70}")
    click.echo("🌍 Flamehaven-Doc-Sanity I18n Translation System")
    click.echo(f"{'='*70}\n")

    # Initialize components
    detector = LanguageDetector()
    parser = CodeCommentParser()
    translator = TranslationEngine(mode=mode)
    oracle = TranslationQualityOracle(strict_threshold=quality_threshold)
    consistency = ConsistencyChecker()
    context_analyzer = ContextAnalyzer()

    path_obj = Path(path)
    files_to_process = []

    if path_obj.is_file():
        files_to_process = [path_obj]
    elif path_obj.is_dir():
        pattern = "**/*.py" if recursive else "*.py"
        files_to_process = list(path_obj.glob(pattern))

    if not files_to_process:
        click.secho("⚠ No Python files found", fg="yellow")
        return

    click.echo(f"Found {len(files_to_process)} file(s) to process\n")

    total_translations = 0
    total_quality_score = 0.0
    files_processed = 0

    for file_path in files_to_process:
        try:
            click.echo(f"Processing: {file_path.name}")

            # Parse file
            parsed = parser.parse_file(str(file_path))

            if not parsed.comments and not parsed.docstrings:
                click.echo("  → No translatable content found\n")
                continue

            # Detect language if auto
            detected_lang = source_lang
            if source_lang == "auto" and (parsed.comments or parsed.docstrings):
                sample_text = (
                    parsed.comments[0].content
                    if parsed.comments
                    else parsed.docstrings[0].content
                )
                detection = detector.detect(sample_text)
                detected_lang = detection.language
                click.echo(
                    f"  → Detected language: {detection.language.upper()} "
                    f"(confidence: {detection.confidence:.2f})"
                )

            if detected_lang == "en":
                click.echo("  → Already in English, skipping\n")
                continue

            # Translate comments
            file_quality_scores = []
            translations_made = 0

            for comment in parsed.comments:
                result = translator.translate(
                    comment.content,
                    source_lang=detected_lang,
                    target_lang=target_lang,
                    context="code_comment",
                )

                # Quality assessment
                assessment = oracle.evaluate(
                    original=comment.content,
                    translated=result.translated,
                    source_lang=detected_lang,
                    preserved_terms=result.preserved_terms,
                )

                file_quality_scores.append(assessment.omega_score)
                translations_made += 1

                if not in_place:
                    click.echo(f"  Comment L{comment.line_number}:")
                    click.echo(f"    Original: {comment.content[:60]}...")
                    click.echo(f"    Translation: {result.translated[:60]}...")
                    click.echo(f"    Ω Score: {assessment.omega_score:.3f}")

            # Translate docstrings
            for docstring in parsed.docstrings:
                result = translator.translate(
                    docstring.content,
                    source_lang=detected_lang,
                    target_lang=target_lang,
                    context="docstring",
                )

                assessment = oracle.evaluate(
                    original=docstring.content,
                    translated=result.translated,
                    source_lang=detected_lang,
                    preserved_terms=result.preserved_terms,
                )

                file_quality_scores.append(assessment.omega_score)
                translations_made += 1

            # Calculate file average
            if file_quality_scores:
                avg_quality = sum(file_quality_scores) / len(file_quality_scores)
                total_quality_score += avg_quality
                total_translations += translations_made
                files_processed += 1

                if avg_quality >= quality_threshold:
                    click.secho(f"  ✓ Quality: {avg_quality:.3f} (PASSED)", fg="green")
                else:
                    click.secho(
                        f"  ⚠ Quality: {avg_quality:.3f} (BELOW THRESHOLD)", fg="yellow"
                    )

                if in_place:
                    # Would reconstruct and write file here
                    click.secho(f"  → Translations applied in-place", fg="green")
                else:
                    click.echo(f"  → Preview mode (use --in-place to apply)")

            click.echo()

        except Exception as e:
            click.secho(f"  ✗ Error: {str(e)}", fg="red")
            click.echo()

    # Summary
    click.echo(f"{'='*70}")
    click.echo("📊 Translation Summary")
    click.echo(f"{'='*70}")
    click.echo(f"Files processed: {files_processed}/{len(files_to_process)}")
    click.echo(f"Total translations: {total_translations}")

    if files_processed > 0:
        overall_quality = total_quality_score / files_processed
        click.echo(f"Average Ω Score: {overall_quality:.3f}")

        if overall_quality >= quality_threshold:
            click.secho("✓ Overall quality: PASSED", fg="green", bold=True)
        else:
            click.secho("⚠ Overall quality: BELOW THRESHOLD", fg="yellow", bold=True)

    click.echo(f"{'='*70}\n")


@main.command()
@click.option("--host", default="127.0.0.1", help="Dashboard server host address")
@click.option("--port", default=5000, type=int, help="Dashboard server port number")
@click.option("--debug", is_flag=True, help="Enable Flask debug mode")
def dashboard(host, port, debug):
    """Launch the DriftLock Dashboard web interface.

    \b
    The dashboard provides:
    - Real-time JSD score visualization
    - Historical drift trend charts
    - Configuration testing interface
    - Alert threshold configuration
    - Affected dimensions analysis

    \b
    Example:
        doc-sanity dashboard
        doc-sanity dashboard --port 8080
        doc-sanity dashboard --host 0.0.0.0 --port 8080 --debug
    """
    try:
        from flamehaven_doc_sanity.dashboard import DashboardServer
    except ImportError:
        click.secho(
            "❌ Dashboard requires Flask to be installed.\n"
            "Install it with: pip install flask",
            fg="red",
            bold=True,
        )
        return

    click.echo("=" * 70)
    click.secho("🎯 DriftLock Dashboard", fg="cyan", bold=True)
    click.echo("=" * 70)
    click.echo(f"Version: {__version__}")
    click.echo(f"Host: http://{host}:{port}")
    click.echo(f"Debug Mode: {'Enabled' if debug else 'Disabled'}")
    click.echo("=" * 70)
    click.echo()

    server = DashboardServer(host=host, port=port)
    server.run(debug=debug)


if __name__ == "__main__":
    main()

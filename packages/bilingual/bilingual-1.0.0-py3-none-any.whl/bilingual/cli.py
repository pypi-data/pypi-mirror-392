"""
Command-line interface for bilingual package.

Provides easy access to common NLP tasks from the terminal.
"""

import argparse
import sys

from bilingual import __version__
from bilingual import bilingual_api as bb


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Bilingual: High-quality Bangla and English NLP toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"bilingual {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Tokenize command
    tokenize_parser = subparsers.add_parser("tokenize", help="Tokenize text")
    tokenize_parser.add_argument("--text", required=True, help="Text to tokenize")
    tokenize_parser.add_argument("--lang", choices=["bn", "en"], help="Language code")
    tokenize_parser.add_argument(
        "--tokenizer", default="bilingual-tokenizer", help="Tokenizer model name"
    )
    tokenize_parser.add_argument(
        "--ids", action="store_true", help="Return token IDs instead of strings"
    )

    # Normalize command
    normalize_parser = subparsers.add_parser("normalize", help="Normalize text")
    normalize_parser.add_argument("--text", required=True, help="Text to normalize")
    normalize_parser.add_argument("--lang", choices=["bn", "en"], help="Language code")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate text")
    generate_parser.add_argument("--prompt", required=True, help="Input prompt")
    generate_parser.add_argument("--model", default="bilingual-small-lm", help="Model name")
    generate_parser.add_argument(
        "--max-tokens", type=int, default=100, help="Maximum tokens to generate"
    )
    generate_parser.add_argument(
        "--temperature", type=float, default=0.7, help="Sampling temperature"
    )
    generate_parser.add_argument(
        "--top-p", type=float, default=0.9, help="Nucleus sampling parameter"
    )

    # Translate command
    translate_parser = subparsers.add_parser("translate", help="Translate text")
    translate_parser.add_argument("--text", required=True, help="Text to translate")
    translate_parser.add_argument(
        "--src", default="bn", choices=["bn", "en"], help="Source language"
    )
    translate_parser.add_argument(
        "--tgt", default="en", choices=["bn", "en"], help="Target language"
    )
    translate_parser.add_argument(
        "--model", default="bilingual-translate", help="Translation model name"
    )

    # Readability command
    readability_parser = subparsers.add_parser("readability", help="Check text readability")
    readability_parser.add_argument("--text", required=True, help="Text to check")
    readability_parser.add_argument("--lang", choices=["bn", "en"], help="Language code")

    # Safety command
    safety_parser = subparsers.add_parser("safety", help="Check text safety")
    safety_parser.add_argument("--text", required=True, help="Text to check")
    safety_parser.add_argument("--lang", choices=["bn", "en"], help="Language code")

    # Evaluate command
    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate model on dataset")
    evaluate_parser.add_argument("--dataset", required=True, help="Path to dataset file")
    evaluate_parser.add_argument("--model", required=True, help="Model name")
    evaluate_parser.add_argument("--metric", default="all", help="Metric to compute")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    try:
        if args.command == "tokenize":
            result = bb.tokenize(args.text, tokenizer=args.tokenizer, return_ids=args.ids)
            print(result)

        elif args.command == "normalize":
            norm_result = bb.normalize_text(args.text, lang=args.lang)
            print(norm_result)

        elif args.command == "generate":
            gen_result = bb.generate(
                args.prompt,
                model_name=args.model,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
            )
            print(gen_result)

        elif args.command == "translate":
            trans_result = bb.translate(
                args.text,
                src=args.src,
                tgt=args.tgt,
                model_name=args.model,
            )
            print(trans_result)

        elif args.command == "readability":
            read_result = bb.readability_check(args.text, lang=args.lang)
            print(f"Level: {read_result['level']}")
            print(f"Age Range: {read_result['age_range']}")
            print(f"Score: {read_result['score']:.2f}")

        elif args.command == "safety":
            safety_result = bb.safety_check(args.text, lang=args.lang)
            print(f"Safe: {safety_result['is_safe']}")
            print(f"Confidence: {safety_result['confidence']:.2f}")
            if safety_result["flags"]:
                print(f"Flags: {', '.join(safety_result['flags'])}")
            print(f"Recommendation: {safety_result['recommendation']}")

        elif args.command == "evaluate":
            from bilingual.evaluation import evaluate_model

            eval_result = evaluate_model(args.dataset, args.model, metric=args.metric)
            print(eval_result)

        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

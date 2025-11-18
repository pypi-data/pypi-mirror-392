"""
TiMEM SDK Command Line Interface

Simple CLI tool for TiMEM operations.
"""

import sys
import json
import argparse
from typing import Optional
from .client import TiMEMClient
from .exceptions import TiMEMError


def create_client(api_key: str, base_url: str) -> TiMEMClient:
    """Create TiMEM client."""
    return TiMEMClient(api_key=api_key, base_url=base_url)


def cmd_health(args):
    """Check TiMEM service health."""
    client = create_client(args.api_key, args.base_url)
    try:
        result = client.health_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except TiMEMError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


def cmd_learn(args):
    """Trigger learning from feedback."""
    client = create_client(args.api_key, args.base_url)
    try:
        result = client.learn(
            domain=args.domain,
            min_case_count=args.min_cases,
            min_adoption_rate=args.min_adoption,
            strategy=args.strategy
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except TiMEMError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


def cmd_recall(args):
    """Recall rules by context."""
    client = create_client(args.api_key, args.base_url)
    try:
        # Parse context from JSON string
        context = json.loads(args.context)
        
        result = client.recall(
            context=context,
            domain=args.domain,
            top_k=args.top_k,
            min_confidence=args.min_confidence
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"Error parsing context JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except TiMEMError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


def cmd_add_memory(args):
    """Add a memory."""
    client = create_client(args.api_key, args.base_url)
    try:
        # Parse content from JSON string
        content = json.loads(args.content)
        tags = args.tags.split(',') if args.tags else None
        
        result = client.add_memory(
            user_id=args.user_id,
            domain=args.domain,
            content=content,
            layer_type=args.layer,
            tags=tags
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"Error parsing content JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except TiMEMError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


def cmd_search_memory(args):
    """Search memories."""
    client = create_client(args.api_key, args.base_url)
    try:
        tags = args.tags.split(',') if args.tags else None
        
        result = client.search_memory(
            user_id=args.user_id if args.user_id else None,
            domain=args.domain if args.domain else None,
            tags=tags,
            limit=args.limit
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except TiMEMError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TiMEM SDK Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--api-key',
        required=True,
        help='TiMEM API key'
    )
    parser.add_argument(
        '--base-url',
        default='http://localhost:8001',
        help='TiMEM Engine base URL (default: http://localhost:8001)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health command
    parser_health = subparsers.add_parser('health', help='Check service health')
    parser_health.set_defaults(func=cmd_health)
    
    # Learn command
    parser_learn = subparsers.add_parser('learn', help='Trigger learning from feedback')
    parser_learn.add_argument('--domain', default='general', help='Business domain')
    parser_learn.add_argument('--min-cases', type=int, default=3, help='Minimum case count')
    parser_learn.add_argument('--min-adoption', type=float, default=0.6, help='Minimum adoption rate')
    parser_learn.add_argument('--strategy', default='adaptive', choices=['single', 'cluster', 'adaptive'], help='Summarization strategy')
    parser_learn.set_defaults(func=cmd_learn)
    
    # Recall command
    parser_recall = subparsers.add_parser('recall', help='Recall rules by context')
    parser_recall.add_argument('--context', required=True, help='Context JSON string')
    parser_recall.add_argument('--domain', default='general', help='Business domain')
    parser_recall.add_argument('--top-k', type=int, default=5, help='Number of top rules')
    parser_recall.add_argument('--min-confidence', type=float, default=0.5, help='Minimum confidence')
    parser_recall.set_defaults(func=cmd_recall)
    
    # Add memory command
    parser_add = subparsers.add_parser('add-memory', help='Add a memory')
    parser_add.add_argument('--user-id', type=int, required=True, help='User ID')
    parser_add.add_argument('--domain', required=True, help='Business domain')
    parser_add.add_argument('--content', required=True, help='Memory content JSON string')
    parser_add.add_argument('--layer', default='L1', help='Memory layer (L1-L5)')
    parser_add.add_argument('--tags', help='Comma-separated tags')
    parser_add.set_defaults(func=cmd_add_memory)
    
    # Search memory command
    parser_search = subparsers.add_parser('search-memory', help='Search memories')
    parser_search.add_argument('--user-id', type=int, help='User ID filter')
    parser_search.add_argument('--domain', help='Domain filter')
    parser_search.add_argument('--tags', help='Comma-separated tags filter')
    parser_search.add_argument('--limit', type=int, default=20, help='Result limit')
    parser_search.set_defaults(func=cmd_search_memory)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()

#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false
INPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)
            JSON_MODE=true
            shift
            ;;
        --input)
            [[ $# -ge 2 ]] || { echo "ERROR: --input requires a file path" >&2; exit 1; }
            INPUT_FILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--json] --input <spec.md>"
            echo "  --json            Output results in JSON format"
            echo "  --input <file>    Explicit input file (must be spec.md under specs/<feature>/)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            if [[ -z "$INPUT_FILE" ]]; then
                INPUT_FILE="$1"
                shift
            else
                echo "ERROR: Unexpected argument '$1'. Use --help for usage." >&2
                exit 1
            fi
            ;;
    esac
done

if [[ -z "$INPUT_FILE" ]]; then
    echo "ERROR: Explicit input file is required. Usage: $0 --json --input specs/<feature>/spec.md" >&2
    exit 1
fi

# Keep only first token so callers may pass "<input-file> [notes...]" through {ARGS}
INPUT_FILE="${INPUT_FILE%% *}"

# Get script directory and load common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Resolve context from explicit input file
eval $(get_feature_paths_from_input_file "$INPUT_FILE" "plan")

# Ensure the feature directory exists
mkdir -p "$FEATURE_DIR"

# Copy plan template if it exists
TEMPLATE="$REPO_ROOT/.specify/templates/plan-template.md"
if [[ -f "$TEMPLATE" ]]; then
    cp "$TEMPLATE" "$IMPL_PLAN"
    echo "Copied plan template to $IMPL_PLAN"
else
    echo "Warning: Plan template not found at $TEMPLATE"
    # Create a basic plan file if template doesn't exist
    touch "$IMPL_PLAN"
fi

# Output results
if $JSON_MODE; then
    printf '{"FEATURE_SPEC":"%s","IMPL_PLAN":"%s","SPECS_DIR":"%s","FEATURE_DIR":"%s","INPUT_FILE_ABS":"%s","BRANCH":"%s","HAS_GIT":"%s"}\n' \
        "$FEATURE_SPEC" "$IMPL_PLAN" "$FEATURE_DIR" "$FEATURE_DIR" "$INPUT_FILE_ABS" "$BRANCH" "$HAS_GIT"
else
    echo "FEATURE_SPEC: $FEATURE_SPEC"
    echo "IMPL_PLAN: $IMPL_PLAN" 
    echo "SPECS_DIR: $FEATURE_DIR"
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "INPUT_FILE_ABS: $INPUT_FILE_ABS"
    echo "BRANCH: $BRANCH"
    echo "HAS_GIT: $HAS_GIT"
fi


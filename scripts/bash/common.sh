#!/usr/bin/env bash
# Common functions and variables for all scripts

# Get repository root, with fallback for non-git repositories
get_repo_root() {
    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        git rev-parse --show-toplevel
    else
        # Fall back to script location for non-git repos
        local script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        (cd "$script_dir/../../.." && pwd)
    fi
}

# Get current branch, with fallback for non-git repositories
get_current_branch() {
    # First check if SPECIFY_FEATURE environment variable is set
    if [[ -n "${SPECIFY_FEATURE:-}" ]]; then
        echo "$SPECIFY_FEATURE"
        return
    fi

    # Then check git if available
    if git rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
        git rev-parse --abbrev-ref HEAD
        return
    fi

    # For non-git repos, try to find the latest feature directory
    local repo_root=$(get_repo_root)
    local specs_dir="$repo_root/specs"

    if [[ -d "$specs_dir" ]]; then
        local latest_feature=""
        local highest=0

        for dir in "$specs_dir"/*; do
            if [[ -d "$dir" ]]; then
                local dirname=$(basename "$dir")
                if [[ "$dirname" =~ ^([0-9]{3})- ]]; then
                    local number=${BASH_REMATCH[1]}
                    number=$((10#$number))
                    if [[ "$number" -gt "$highest" ]]; then
                        highest=$number
                        latest_feature=$dirname
                    fi
                fi
            fi
        done

        if [[ -n "$latest_feature" ]]; then
            echo "$latest_feature"
            return
        fi
    fi

    echo "main"  # Final fallback
}

# Check if we have git available
has_git() {
    git rev-parse --show-toplevel >/dev/null 2>&1
}

check_feature_branch() {
    local branch="$1"
    local has_git_repo="$2"

    # For non-git repos, we can't enforce branch naming but still provide output
    if [[ "$has_git_repo" != "true" ]]; then
        echo "[specify] Warning: Git repository not detected; skipped branch validation" >&2
        return 0
    fi

    if [[ ! "$branch" =~ ^[0-9]{3}- ]]; then
        echo "ERROR: Not on a feature branch. Current branch: $branch" >&2
        echo "Feature branches should be named like: 001-feature-name" >&2
        return 1
    fi

    return 0
}

get_feature_dir() { echo "$1/specs/$2"; }

# Find feature directory by numeric prefix instead of exact branch match
# This allows multiple branches to work on the same spec (e.g., 004-fix-bug, 004-add-feature)
find_feature_dir_by_prefix() {
    local repo_root="$1"
    local branch_name="$2"
    local specs_dir="$repo_root/specs"

    # Extract numeric prefix from branch (e.g., "004" from "004-whatever")
    if [[ ! "$branch_name" =~ ^([0-9]{3})- ]]; then
        # If branch doesn't have numeric prefix, fall back to exact match
        echo "$specs_dir/$branch_name"
        return
    fi

    local prefix="${BASH_REMATCH[1]}"

    # Search for directories in specs/ that start with this prefix
    local matches=()
    if [[ -d "$specs_dir" ]]; then
        for dir in "$specs_dir"/"$prefix"-*; do
            if [[ -d "$dir" ]]; then
                matches+=("$(basename "$dir")")
            fi
        done
    fi

    # Handle results
    if [[ ${#matches[@]} -eq 0 ]]; then
        # No match found - return the branch name path (will fail later with clear error)
        echo "$specs_dir/$branch_name"
    elif [[ ${#matches[@]} -eq 1 ]]; then
        # Exactly one match - perfect!
        echo "$specs_dir/${matches[0]}"
    else
        # Multiple matches - this shouldn't happen with proper naming convention
        echo "ERROR: Multiple spec directories found with prefix '$prefix': ${matches[*]}" >&2
        echo "Please ensure only one spec directory exists per numeric prefix." >&2
        echo "$specs_dir/$branch_name"  # Return something to avoid breaking the script
    fi
}

get_feature_paths() {
    local repo_root=$(get_repo_root)
    local current_branch=$(get_current_branch)
    local has_git_repo="false"

    if has_git; then
        has_git_repo="true"
    fi

    # Use prefix-based lookup to support multiple branches per spec
    local feature_dir=$(find_feature_dir_by_prefix "$repo_root" "$current_branch")

    cat <<EOF
REPO_ROOT='$repo_root'
CURRENT_BRANCH='$current_branch'
HAS_GIT='$has_git_repo'
FEATURE_DIR='$feature_dir'
FEATURE_SPEC='$feature_dir/spec.md'
IMPL_PLAN='$feature_dir/plan.md'
TASKS='$feature_dir/tasks.md'
RESEARCH='$feature_dir/research.md'
DATA_MODEL='$feature_dir/data-model.md'
QUICKSTART='$feature_dir/quickstart.md'
CONTRACTS_DIR='$feature_dir/contracts'
EOF
}

# Resolve input file to absolute path (repo-root relative or absolute).
resolve_input_file_abs() {
    local repo_root="$1"
    local input_file="$2"

    if [[ -z "$input_file" ]]; then
        echo "ERROR: input file is required" >&2
        return 1
    fi

    local candidate
    if [[ "$input_file" = /* ]]; then
        candidate="$input_file"
    else
        candidate="$repo_root/$input_file"
    fi

    local parent
    parent="$(dirname "$candidate")"
    local base
    base="$(basename "$candidate")"

    if [[ ! -d "$parent" ]]; then
        echo "ERROR: Input file parent directory does not exist: $parent" >&2
        return 1
    fi

    echo "$(cd "$parent" && pwd)/$base"
}

# Derive feature directory from explicit input file path.
resolve_feature_dir_from_input_file() {
    local repo_root="$1"
    local input_file_abs="$2"

    if [[ ! -f "$input_file_abs" ]]; then
        echo "ERROR: Input file does not exist: $input_file_abs" >&2
        return 1
    fi

    local specs_root="$repo_root/specs/"
    if [[ "$input_file_abs" != "$specs_root"* ]]; then
        echo "ERROR: Input file must be under specs/<feature>/: $input_file_abs" >&2
        return 1
    fi

    local feature_dir
    feature_dir="$(dirname "$input_file_abs")"

    if [[ "$feature_dir" != "$specs_root"* ]]; then
        echo "ERROR: Failed to derive feature directory from input file: $input_file_abs" >&2
        return 1
    fi

    echo "$feature_dir"
}

# Validate allowed input file basenames by mode.
validate_input_file_for_mode() {
    local mode="$1"
    local input_file_abs="$2"
    local input_basename
    input_basename="$(basename "$input_file_abs")"

    case "$mode" in
        ""|generic)
            ;;
        plan|design)
            [[ "$input_basename" == "spec.md" ]] || {
                echo "ERROR: Mode '$mode' requires input basename 'spec.md', got '$input_basename'" >&2
                return 1
            }
            ;;
        tasks|agent_context)
            [[ "$input_basename" == "plan.md" ]] || {
                echo "ERROR: Mode '$mode' requires input basename 'plan.md', got '$input_basename'" >&2
                return 1
            }
            ;;
        preview)
            [[ "$input_basename" == "spec.md" || "$input_basename" == "plan.md" || "$input_basename" == "tasks.md" ]] || {
                echo "ERROR: Mode 'preview' requires input basename spec.md|plan.md|tasks.md, got '$input_basename'" >&2
                return 1
            }
            ;;
        analyze)
            [[ "$input_basename" == "plan.md" || "$input_basename" == "tasks.md" ]] || {
                echo "ERROR: Mode 'analyze' requires input basename plan.md|tasks.md, got '$input_basename'" >&2
                return 1
            }
            ;;
        implement)
            [[ "$input_basename" == "tasks.md" ]] || {
                echo "ERROR: Mode 'implement' requires input basename 'tasks.md', got '$input_basename'" >&2
                return 1
            }
            ;;
        *)
            echo "ERROR: Unknown mode '$mode'" >&2
            return 1
            ;;
    esac
}

# Resolve feature context from explicit input file.
get_feature_paths_from_input_file() {
    local input_file="$1"
    local mode="${2:-}"

    local repo_root
    repo_root="$(get_repo_root)"

    local has_git_repo="false"
    if has_git; then
        has_git_repo="true"
    fi

    local input_file_abs
    input_file_abs="$(resolve_input_file_abs "$repo_root" "$input_file")" || return 1

    local feature_dir
    feature_dir="$(resolve_feature_dir_from_input_file "$repo_root" "$input_file_abs")" || return 1

    validate_input_file_for_mode "$mode" "$input_file_abs" || return 1

    local input_basename
    input_basename="$(basename "$input_file_abs")"

    local feature_name
    feature_name="$(basename "$feature_dir")"

    cat <<EOF
REPO_ROOT='$repo_root'
CURRENT_BRANCH='$feature_name'
BRANCH='$feature_name'
HAS_GIT='$has_git_repo'
INPUT_FILE='$input_file'
INPUT_FILE_ABS='$input_file_abs'
INPUT_BASENAME='$input_basename'
FEATURE_DIR='$feature_dir'
FEATURE_SPEC='$feature_dir/spec.md'
IMPL_PLAN='$feature_dir/plan.md'
TASKS='$feature_dir/tasks.md'
RESEARCH='$feature_dir/research.md'
DATA_MODEL='$feature_dir/data-model.md'
QUICKSTART='$feature_dir/quickstart.md'
CONTRACTS_DIR='$feature_dir/contracts'
EOF
}

check_file() { [[ -f "$1" ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
check_dir() { [[ -d "$1" && -n $(ls -A "$1" 2>/dev/null) ]] && echo "  ✓ $2" || echo "  ✗ $2"; }


#!/bin/bash
# detect-python-env.sh - Cross-platform Python environment detection
#
# Usage: source detect-python-env.sh
#        or: ./detect-python-env.sh [--json]
#
# Sets these variables when sourced:
#   PYTHON_CMD     - Path to Python 3.10+ executable
#   PYTHON_VERSION - Version string (e.g., "3.12.3")
#   PYTHON_SOURCE  - How Python was found (pyenv|mise|brew|system)
#   PYTHON_OK      - "yes" if suitable Python found, "no" otherwise
#   PYTHON_RECOMMENDATION - What to do if PYTHON_OK is "no"

MIN_PYTHON_VERSION="3.10"

# Color output (disable with NO_COLOR=1)
if [[ -z "$NO_COLOR" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Darwin*) echo "macos" ;;
        Linux*)  echo "linux" ;;
        *)       echo "unknown" ;;
    esac
}

# Compare version strings (returns 0 if $1 >= $2)
version_gte() {
    [ "$(printf '%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

# Extract major.minor from version string
get_minor_version() {
    echo "$1" | grep -oE '^[0-9]+\.[0-9]+'
}

# Check a Python executable
check_python() {
    local python_cmd="$1"
    local source="$2"

    if [[ ! -x "$python_cmd" ]] && ! command -v "$python_cmd" &>/dev/null; then
        return 1
    fi

    local version
    version=$("$python_cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')

    if [[ -z "$version" ]]; then
        return 1
    fi

    local minor_version
    minor_version=$(get_minor_version "$version")

    if version_gte "$minor_version" "$MIN_PYTHON_VERSION"; then
        PYTHON_CMD="$python_cmd"
        PYTHON_VERSION="$version"
        PYTHON_SOURCE="$source"
        PYTHON_OK="yes"
        return 0
    fi

    return 1
}

# Main detection logic
detect_python() {
    local os_type
    os_type=$(detect_os)

    PYTHON_CMD=""
    PYTHON_VERSION=""
    PYTHON_SOURCE=""
    PYTHON_OK="no"
    PYTHON_RECOMMENDATION=""

    # Detection order:
    # - pyenv first (explicit Python version manager - user made deliberate choice)
    # - Homebrew on macOS (platform standard, very common)
    # - mise (newer polyglot manager)
    # - system Python (last resort)

    # 1. Check pyenv first (respects user's explicit choice)
    if command -v pyenv &>/dev/null; then
        local pyenv_python
        pyenv_python=$(pyenv which python3 2>/dev/null)
        if [[ -n "$pyenv_python" ]] && check_python "$pyenv_python" "pyenv"; then
            return 0
        fi
        # pyenv exists but no suitable version
        if [[ "$PYTHON_OK" != "yes" ]]; then
            PYTHON_RECOMMENDATION="pyenv install 3.12 && pyenv global 3.12"
        fi
    fi

    # 2. Check Homebrew (macOS only) - platform standard, very common
    if [[ "$os_type" == "macos" ]]; then
        local brew_prefix
        if [[ -x /opt/homebrew/bin/brew ]]; then
            brew_prefix="/opt/homebrew"
        elif [[ -x /usr/local/bin/brew ]]; then
            brew_prefix="/usr/local"
        fi

        if [[ -n "$brew_prefix" ]]; then
            # Check for python@3.12 or python@3.11 first (Homebrew uses versioned names)
            for ver in 3.12 3.11 3.10; do
                # Homebrew python binary is named python3.X, not python3
                local brew_python="$brew_prefix/opt/python@$ver/bin/python$ver"
                if check_python "$brew_python" "brew"; then
                    return 0
                fi
            done
            # Check generic brew python3 (if user ran `brew install python3`)
            if check_python "$brew_prefix/bin/python3" "brew"; then
                return 0
            fi
            # Homebrew exists but no suitable Python
            if [[ "$PYTHON_OK" != "yes" && -z "$PYTHON_RECOMMENDATION" ]]; then
                PYTHON_RECOMMENDATION="brew install python@3.12"
            fi
        fi
    fi

    # 3. Check mise (polyglot version manager)
    if command -v mise &>/dev/null || [[ -x /opt/homebrew/bin/mise ]] || [[ -x ~/.local/bin/mise ]]; then
        local mise_cmd
        if command -v mise &>/dev/null; then
            mise_cmd="mise"
        elif [[ -x /opt/homebrew/bin/mise ]]; then
            mise_cmd="/opt/homebrew/bin/mise"
        elif [[ -x ~/.local/bin/mise ]]; then
            mise_cmd="$HOME/.local/bin/mise"
        fi

        if [[ -n "$mise_cmd" ]]; then
            local mise_python
            mise_python=$($mise_cmd which python3 2>/dev/null)
            if [[ -n "$mise_python" ]] && check_python "$mise_python" "mise"; then
                return 0
            fi
            # mise exists but no suitable version
            if [[ "$PYTHON_OK" != "yes" && -z "$PYTHON_RECOMMENDATION" ]]; then
                PYTHON_RECOMMENDATION="mise use python@3.12"
            fi
        fi
    fi

    # 4. Check system Python
    for python_cmd in python3 python; do
        if check_python "$python_cmd" "system"; then
            return 0
        fi
    done

    # 5. No suitable Python found - set recommendation based on OS
    if [[ -z "$PYTHON_RECOMMENDATION" ]]; then
        case "$os_type" in
            macos)
                if command -v brew &>/dev/null || [[ -x /opt/homebrew/bin/brew ]]; then
                    PYTHON_RECOMMENDATION="brew install python@3.12"
                else
                    PYTHON_RECOMMENDATION="Install Homebrew first: https://brew.sh, then: brew install python@3.12"
                fi
                ;;
            linux)
                if command -v apt-get &>/dev/null; then
                    PYTHON_RECOMMENDATION="sudo apt-get install python3.12 python3.12-venv"
                elif command -v dnf &>/dev/null; then
                    PYTHON_RECOMMENDATION="sudo dnf install python3.12"
                else
                    PYTHON_RECOMMENDATION="Install mise: curl https://mise.run | sh && mise use python@3.12"
                fi
                ;;
            *)
                PYTHON_RECOMMENDATION="Install Python 3.10+ from https://python.org"
                ;;
        esac
    fi

    return 1
}

# Output results
print_results() {
    local json_output="$1"

    if [[ "$json_output" == "--json" ]]; then
        cat <<EOF
{
  "python_ok": "$PYTHON_OK",
  "python_cmd": "$PYTHON_CMD",
  "python_version": "$PYTHON_VERSION",
  "python_source": "$PYTHON_SOURCE",
  "recommendation": "$PYTHON_RECOMMENDATION",
  "os": "$(detect_os)"
}
EOF
    else
        echo -e "${BLUE}Python Environment Detection${NC}"
        echo "=============================="
        echo "OS: $(detect_os)"
        echo ""

        if [[ "$PYTHON_OK" == "yes" ]]; then
            echo -e "${GREEN}✓ Found suitable Python${NC}"
            echo "  Command: $PYTHON_CMD"
            echo "  Version: $PYTHON_VERSION"
            echo "  Source:  $PYTHON_SOURCE"
        else
            echo -e "${RED}✗ No suitable Python found${NC}"
            echo "  Required: Python >= $MIN_PYTHON_VERSION"
            echo ""
            echo -e "${YELLOW}Recommendation:${NC}"
            echo "  $PYTHON_RECOMMENDATION"
        fi
    fi
}

# Run detection
detect_python

# If script is executed (not sourced), print results
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    print_results "$1"
    exit $([[ "$PYTHON_OK" == "yes" ]] && echo 0 || echo 1)
fi

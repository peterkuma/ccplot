# libtest.sh
# Minimal testing framework.
#
# Example:
#
# testing "command with arguments arg1 arg2, ..." 
# check command arg1 arg2 [...]
# expect <<EOF
# Expected output
# EOF
# 
# [...]
#
# complete
#

TESTING=0
RESULT=0
SKIPPED=0
PASSED=0
FAILED=0
INT=0
OUTPUT=""

if [ -t 1 ]; then
    # Use colors if stdin is a terminal.
    BOLD="\033[1m"
    GREEN="\033[32m"
    BROWN="\033[33m"
    RED="\033[31m"
    GREY="\033[37m"
    Q="\033[0m"
else
    exec 2>&1
fi

# testing LABEL
#
# Start new test with label LABEL.
testing() {
    finish_previous

    TESTING=1
    [ $(($PASSED + $FAILED)) -gt 0 ] && echo
    echo "Testing $1"
}

# check CMD [ARG]...
#
# Test return status of command CMD with given arguments.
check() {
    [ $TESTING -eq 0 -o $RESULT -gt 0 ] && return
    echo "$@"
    trap 'echo; INT=1' 2
    OUTPUT="$($@ 2>&1)"
    EXIT=$?
    trap 2
    RESULT=$((RESULT | $EXIT))
    #[ $EXIT -ne 0 ] && echo "$OUTPUT"
    echo -n "$GREY"
    [ -n "$OUTPUT" ] && echo "$OUTPUT"
    echo -n "$Q"
}

# expect OUTPUT
# expect <<EOF
# OUTPUT
# EOF
#
# Check if ouput of the previous check command matches OUTPUT.
expect() {
    if [ $# -eq 0 ]; then
        STRING="$(cat)"
    else
        STRING="$1"
    fi
    [ $TESTING -eq 0 -o $RESULT -gt 0 ] && return
    [ "$OUTPUT" = "$STRING" ]
    R=$?
    if [ $R -ne 0 ]; then
        echo "---- Expected ----"
        echo "${GREY}$STRING${Q}"
    fi
    RESULT=$((RESULT | $R))
}

# complete
#
# Finish testing, and print statistics.
complete() {
    finish_previous
    [ $(($PASSED + $FAILED)) -gt 0 ] && echo
    echo "$SKIPPED tests SKIPPED, $PASSED tests PASSED, $FAILED tests FAILED"
    if [ $FAILED -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

finish_previous() {
    [ $TESTING -eq 0 ] && return
    if [ $INT -eq 1 ]; then
        echo "${BROWN}SKIPPED${Q}"
        SKIPPED=$((SKIPPED+1))
    elif [ $RESULT -eq 0 ]; then
        echo "${GREEN}PASSED${Q}"
        PASSED=$((PASSED+1))
    else
        echo "${RED}FAILED${Q}"
        FAILED=$((FAILED+1))
    fi
    TESTING=0
    RESULT=0
    INT=0
}


#!/bin/bash
# Monitor system resources during stress test
# Usage: ./tests/monitor.sh

echo "=== PromptMe-Lite Resource Monitor ==="
echo "Monitoring all challenge ports... (Press Ctrl+C to stop)"
echo ""

while true; do
    clear
    echo "=== PromptMe-Lite Resource Monitor ==="
    date
    echo ""

    # Check all challenge ports
    echo "Challenge Status:"
    for port in 5001 5002 5003 5004 5005 5006 5007 5008 5009 5010; do
        if lsof -i :$port > /dev/null 2>&1; then
            pid=$(lsof -t -i :$port)
            mem=$(ps -o rss= -p $pid 2>/dev/null | awk '{print $1/1024 " MB"}')
            cpu=$(ps -o %cpu= -p $pid 2>/dev/null)
            echo "  Port $port (PID $pid): CPU ${cpu}%, MEM $mem"
        else
            echo "  Port $port: NOT RUNNING"
        fi
    done

    echo ""
    echo "=== System Resources ==="

    # macOS-specific commands
    if [[ "$OSTYPE" == "darwin"* ]]; then
        top -l 1 | grep -E "^CPU|^PhysMem"
    else
        # Linux
        top -b -n 1 | grep -E "^%Cpu|^MiB Mem"
    fi

    echo ""
    echo "=== Network Connections ==="
    netstat -an 2>/dev/null | grep -E "500[0-9]|5010" | grep ESTABLISHED | wc -l | awk '{print "Active connections: " $1}'

    sleep 2
done

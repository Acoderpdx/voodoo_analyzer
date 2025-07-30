#!/bin/bash
# Launch the analyzer in background and keep it running

cd "$(dirname "$0")"
echo "🚀 Starting Plugin Analyzer in background..."
echo "The GUI window will appear on your screen."
echo ""

# Run in background with nohup
nohup python main.py > analyzer.log 2>&1 &
PID=$!

echo "✅ Analyzer started with PID: $PID"
echo ""
echo "📝 Logs are being written to: analyzer.log"
echo "   You can check logs with: tail -f analyzer.log"
echo ""
echo "🛑 To stop the analyzer later, run:"
echo "   kill $PID"
echo ""
echo "The analyzer is now running in the background!"
echo "Look for the 'Plugin Parameter Discovery' window."
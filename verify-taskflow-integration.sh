#!/bin/bash
# Verification script for TaskFlow-WebGen integration
# Usage: ./verify-taskflow-integration.sh

set -e

echo "🔍 Verifying TaskFlow-WebGen Integration..."
echo ""

ERRORS=0

# Check WebGen plugin structure
echo "📦 Checking WebGen plugin structure..."

if [ ! -f "plugins/webgen/.claude-plugin/plugin.json" ]; then
  echo "❌ WebGen plugin.json not found"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ WebGen plugin.json exists"
fi

if [ ! -f "plugins/webgen/agents/webgen-orchestrator.md" ]; then
  echo "❌ WebGen orchestrator not found"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ WebGen orchestrator exists"
fi

if [ ! -f "plugins/webgen/skills/taskflow-integration/skill.md" ]; then
  echo "❌ TaskFlow integration skill not found"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ TaskFlow integration skill exists"
fi

if [ ! -f "plugins/webgen/docs/TASKFLOW-INTEGRATION.md" ]; then
  echo "❌ TaskFlow integration docs not found"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ TaskFlow integration docs exist"
fi

echo ""
echo "📝 Checking plugin.json configuration..."

# Check version
VERSION=$(grep '"version"' plugins/webgen/.claude-plugin/plugin.json | head -1 | grep -o '"[^"]*"' | tail -1 | tr -d '"')
if [ "$VERSION" != "1.5.0" ]; then
  echo "❌ Version is $VERSION, expected 1.5.0"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ Version is 1.5.0"
fi

# Check skills array includes taskflow-integration
if grep -q '"taskflow-integration"' plugins/webgen/.claude-plugin/plugin.json; then
  echo "✅ taskflow-integration in skills array"
else
  echo "❌ taskflow-integration NOT in skills array"
  ERRORS=$((ERRORS + 1))
fi

echo ""
echo "📄 Checking documentation updates..."

# Check README mentions TaskFlow
if grep -q "TaskFlow Integration" plugins/webgen/README.md; then
  echo "✅ README mentions TaskFlow integration"
else
  echo "❌ README missing TaskFlow integration mention"
  ERRORS=$((ERRORS + 1))
fi

# Check CHANGELOG has v1.5.0
if grep -q "\[1.5.0\]" plugins/webgen/docs/CHANGELOG.md; then
  echo "✅ CHANGELOG includes v1.5.0 entry"
else
  echo "❌ CHANGELOG missing v1.5.0 entry"
  ERRORS=$((ERRORS + 1))
fi

# Check orchestrator mentions TaskFlow
if grep -q "TaskFlow Integration" plugins/webgen/agents/webgen-orchestrator.md; then
  echo "✅ Orchestrator includes TaskFlow integration"
else
  echo "❌ Orchestrator missing TaskFlow integration"
  ERRORS=$((ERRORS + 1))
fi

echo ""
echo "🔗 Checking TaskFlow plugin presence..."

if [ -d "plugins/taskflow" ]; then
  echo "✅ TaskFlow plugin found"

  if [ -f "plugins/taskflow/README.md" ]; then
    echo "✅ TaskFlow README exists"
  else
    echo "⚠️  TaskFlow README not found (non-critical)"
  fi
else
  echo "⚠️  TaskFlow plugin not found (integration will work when installed)"
fi

echo ""
echo "📊 Summary:"
echo "───────────────────────────────────────"

if [ $ERRORS -eq 0 ]; then
  echo "✅ All checks passed!"
  echo ""
  echo "Integration is properly configured."
  echo ""
  echo "Next steps:"
  echo "1. Test without TaskFlow installed (should work normally)"
  echo "2. Install TaskFlow and test detection"
  echo "3. Test opt-in workflow"
  echo "4. Test task creation and status updates"
  exit 0
else
  echo "❌ $ERRORS error(s) found"
  echo ""
  echo "Please review the errors above and fix before deploying."
  exit 1
fi

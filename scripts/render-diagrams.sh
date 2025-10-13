#!/usr/bin/env bash
set -euo pipefail

echo "Rendering PlantUML diagrams (bash)"
root="$(dirname "$0")"
cd "$root/.."

workspace="$(pwd)"
outDir="$workspace/docs/diagrams/generated"
mkdir -p "$outDir"

echo "Using Docker image plantuml/plantuml to render files..."

docker run --rm -v "$workspace":/workspace plantuml/plantuml:latest -tpng docs/diagrams/*.puml -o docs/diagrams/generated

echo "Rendered diagrams saved to: $outDir"
echo "You can commit the generated files if you want them tracked in the repo."
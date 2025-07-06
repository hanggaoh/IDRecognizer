workingDir="$(dirname "$(dirname "$0")")"

cd "$workingDir"
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi
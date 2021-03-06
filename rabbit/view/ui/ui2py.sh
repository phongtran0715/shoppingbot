ui_files=$(find . -type f -name "*.ui")
count=0
while IFS= read -r f_ui; do
	f_py=$(basename "$f_ui" | cut -f 1 -d .)".py"
	pyuic5 "$f_ui" -o "$f_py"
	count=$((count + 1))
done < <(printf '%s\n' "$ui_files")
echo "Converted $count file!"

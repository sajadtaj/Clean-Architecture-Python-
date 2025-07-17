#!/bin/bash

# فایل خروجی
OUTPUT_FILE="project_structure_documentation.md"

# پاک‌سازی فایل خروجی
> "$OUTPUT_FILE"

# تیتر اصلی
echo "# 🧱 Clean Architecture Project Structure" >> "$OUTPUT_FILE"
echo "📁 Root: \`src/crypto_option_arbitrage\`" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"

# تابع بازگشتی برای پیمایش ساختار
generate_structure() {
    local indent="$1"
    local path="$2"

    for item in "$path"/*; do
        # رد فایل‌ها یا پوشه‌های غیرضروری
        [[ "$(basename "$item")" == "__pycache__" ]] && continue
        [[ "$(basename "$item")" == "generate_project_structure.sh" ]] && continue
        [[ "$(basename "$item")" == .* ]] && continue

        if [[ -d "$item" ]]; then
            # نمایش عنوان لایه
            title_name=$(basename "$item" | sed 's/_/ /g' | sed -E 's/\b(.)/\U\1/g')
            echo "" >> "$OUTPUT_FILE"
            echo "## 🗂️ Layer: $title_name" >> "$OUTPUT_FILE"
            echo "📂 Path: \`$(realpath --relative-to=. "$item")\`" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            generate_structure "$indent  " "$item"
        elif [[ -f "$item" ]]; then
            file_name=$(basename "$item")
            rel_path=$(realpath --relative-to=. "$item")

            echo "- **File**: \`$file_name\`" >> "$OUTPUT_FILE"
            echo "  - 📍 Path: \`$rel_path\`" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"

            echo '```python' >> "$OUTPUT_FILE"
            cat "$item" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    done
}

# اجرای تابع اصلی روی دایرکتوری جاری
generate_structure "" "."

# پیام موفقیت
echo -e "\n✅ Documentation generated at: $OUTPUT_FILE"

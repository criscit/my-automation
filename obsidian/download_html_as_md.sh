#!/bin/bash

# Set output folder path
OUTPUT_DIR=~/OneDrive/Desktop/exported_newsletters
mkdir -p "$OUTPUT_DIR"

# Declare an associative array with link text as key and URL as value
declare -A pages=(
  ["How to Adjust to the Fall Time Change"]="https://e.mail.ru/message/17305653641231669512/print/?folder_id=500013&open-multipage-name=read-letter&self-id=7a0099d9-7e61-2fd8-dafd-d476e5a67d27&parent-id=MailMainPage"  
  ["How to Beat Jet Lag"]="https://e.mail.ru/message/17323779022090341968/print/?folder_id=500013&open-multipage-name=read-letter&self-id=94b3d052-1aea-f25-926b-180b7013c51a&parent-id=MailMainPage"
)

# Loop through the array and run pandoc
for name in "${!pages[@]}"; do
  url="${pages[$name]}"
  output_file="${OUTPUT_DIR}/${name}.md"
  echo "Converting: $url → $output_file"
  pandoc -f html -t markdown -o "$output_file" "$url"
done

echo "✅ All files saved to $OUTPUT_DIR"

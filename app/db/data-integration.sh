for file in static/selecta/*; do cwebp -q 100 "$file" -o "${file%.*}.webp"; done

rm static/selecta/*.jpg
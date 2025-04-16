#!/bin/bash

languages=("en" "zh" "fr" "es" "de" "el" "bg" "ru" "tr" "ar" "vi" "th" "hi" "sw" "ur")

for language in "${languages[@]}"; do
    echo "Processing language: $language"

    cd search_engine
    mkdir -p "$language"
    cp run_indexing.sh "$language"
    cd "$language"
    chmod +x ./run_indexing.sh
    mkdir -p resources resources_100 resources_1k resources_100k
    cd ..
    python convert_product_file_format.py --language "$language"
    cd "$language"
    mkdir -p indexes
    ./run_indexing.sh
    cd ..
    cd ..
    echo "Finished processing language: $language"
    echo ""
done
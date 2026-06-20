#!/bin/bash
# Build script for resume template
# Usage: bash build.sh
# Or for a specific file: tectonic output/your_resume.tex

# Compile the template
tectonic resume_template.tex

# Open the PDF (macOS)
# Uncomment the line for your OS:
open -a "Preview" resume_template.pdf        # macOS (Preview)
# open -a "Google Chrome" resume_template.pdf  # macOS (Chrome)
# xdg-open resume_template.pdf                 # Linux
# start resume_template.pdf                    # Windows

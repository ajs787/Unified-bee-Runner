#!/usr/bin/env bash
set -euo pipefail

# List all your submodule paths here:
submodules=(
  VideoSamplerRewrite
  Video_Frame_Counter
  Video_Subtractions
  bee_analysis
  non_workflow_links/DataCropping
  non_workflow_links/Pi-Code
  non_workflow_links/ai-for-behavioral-discovery
  non_workflow_links/working_bee_analysis
)

for m in "${submodules[@]}"; do
  echo "=== Converting $m … ==="

  # 1) Snapshot the current files
  cp -r "$m" "${m}.tmp"

  # 2) Unregister as submodule (metadata stays in .git until we remove it)
  git submodule deinit -f -- "$m"

  # 3) Remove the gitlink from the index
  git rm --cached "$m"

  # 4) Remove the .gitmodules entry
  git config -f .gitmodules --remove-section submodule."$m" || true

  # 5) Delete the submodule’s metadata folder
  rm -rf ".git/modules/$m"

  # 6) Wipe any empty placeholder folder
  rm -rf "$m"

  # 7) Restore your real files
  mv "${m}.tmp" "$m"

  # 8) Stage the new directory and updated .gitmodules
  git add "$m" .gitmodules

  # 9) Commit the conversion
  git commit -m "Convert $m from submodule to regular directory"
done

# Finally, push all those commits at once
git push

#!/bin/bash

REPOSITORY='--repository testpypi'

rm -rf debugmate.egg-info
rm -rf dist
rm -rf venv

python3 -m venv venv

source venv/bin/activate

python3 -m pip install --upgrade build twine

python3 -m build

echo -e 'You want build to Pypi or Test.pypi:'
options=("Test.pypi", "Pypi")
select repository_option in "${options[@]}"; do
  if [[ -n "$repository_option" ]]; then
    if [[ "$repository_option" == "Pypi" ]]; then
      REPOSITORY=''
    fi
    break
  fi
  echo "Invalid selection, please try again."
done

python3 -m twine upload $REPOSITORY dist/*
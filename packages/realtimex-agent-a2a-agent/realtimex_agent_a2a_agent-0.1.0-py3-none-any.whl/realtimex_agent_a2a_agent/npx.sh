#!/bin/bash
export NVM_DIR=/Users/$(whoami)/.nvm
source $NVM_DIR/nvm.sh

npx "$@"
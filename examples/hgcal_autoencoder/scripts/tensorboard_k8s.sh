#!/bin/bash

tmux new-session -d -s tb "kubectl port-forward tboard 8008:8008"


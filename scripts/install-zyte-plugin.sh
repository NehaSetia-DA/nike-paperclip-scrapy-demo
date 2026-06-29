#!/usr/bin/env bash
set -euo pipefail

claude plugin marketplace add zytedata/claude-skills
claude plugin install zyte-web-data@zyte-ai
claude plugin list


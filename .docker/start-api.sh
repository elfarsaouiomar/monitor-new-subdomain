#!/usr/bin/bash

cd /app/src

uvicorn API:app --reload --reload-dir http/
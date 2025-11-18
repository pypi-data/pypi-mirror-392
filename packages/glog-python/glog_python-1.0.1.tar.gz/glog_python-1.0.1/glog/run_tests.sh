#!/bin/bash

echo "Running PyLog Tests..."
echo "====================="
echo ""

echo "Running unit tests..."
python3 pylog/tests/test_logger.py
python3 pylog/tests/test_context_logger.py

echo ""
echo "Running examples..."
echo "-------------------"
echo ""

echo "Basic example:"
python3 pylog/examples/basic_example.py

echo ""
echo "Context example:"
python3 pylog/examples/context_example.py

echo ""
echo "All tests completed!"

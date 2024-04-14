# Get the directory of the current Makefile
MAKEFILE_PATH := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
REVA_PYTHON_PATH := $(MAKEFILE_PATH)/reverse-engineering-assistant/reverse_engineering_assistant

.PHONY: protocol ghidra python all clean

all: protocol ghidra python
clean:
	rm -rf $(REVA_PYTHON_PATH)/protocol
	rm -rf reverse-engineering-assistant/dist reverse-engineering-assistant/build
	rm -rf ghidra-assistant/build ghidra-assistant/dist

ghidra: protocol
	gradle -b $(MAKEFILE_PATH)/ghidra-assistant/build.gradle

python: protocol
	python3 -m pip install build
	python3 -m build reverse-engineering-assistant

protocol:
	# Generate Python code from proto file
	python3 -m pip install -r $(MAKEFILE_PATH)/requirements.txt
	python3 -m grpc_tools.protoc \
		--proto_path=. \
		--python_out=$(REVA_PYTHON_PATH) \
		--pyi_out=$(REVA_PYTHON_PATH) \
		--grpc_python_out=$(REVA_PYTHON_PATH) \
		protocol/*.proto
	touch $(REVA_PYTHON_PATH)/protocol/__init__.py

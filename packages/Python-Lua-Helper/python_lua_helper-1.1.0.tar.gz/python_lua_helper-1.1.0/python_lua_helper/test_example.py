#!/usr/bin/env python3

import os
import sys
from py_lua_helper import PyLuaHelper

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

print("example.py: creating PyLuaHelper instance")

# Create PyLuaHelper instance with same parameters as example.bash
cfg = PyLuaHelper(
    lua_config_script=os.path.join(script_dir, "test_example", "example.cfg.lua"),
    export_vars=["config.sub", "config.paths", "config.empty", "wrong.table", "empty"],
    extra_strings=["test1", "test2"],
    pre_script=os.path.join(script_dir, "test_example", "example.pre.lua"),
    post_script=os.path.join(script_dir, "test_example", "example.post.lua"),
    work_dir=script_dir,
    lua_args=sys.argv[1:]
)

print("example.py: PyLuaHelper complete")
print(f"example.py: my own cmdline params={sys.argv[1:]}")
print("")
print("example.py: names of all global variables exported from lua script:")
print(cfg.keys())
print("")

# Check variable availability
print("example.py: === value availability tests ===")
print("example.py: check for config.empty variable availability is ", end="")
try:
    if "config.empty" in cfg:
        print("passed, but should fail !!!")
    else:
        print("failed, as expected")
except Exception:
    print("failed (exception)")

print("example.py: check for wrong.table variable availability is ", end="")
try:
    if "wrong.table" in cfg:
        print("passed, but should fail !!!")
    else:
        print("failed, as expected")
except Exception:
    print("failed (exception)")

print("example.py: check for empty variable availability is ", end="")
try:
    if "empty" in cfg:
        print("passed, but should fail !!!")
    else:
        print("failed, as expected")
except Exception:
    print("failed (exception)")

print("example.py: check for config.value variable availability is ", end="")
try:
    if "config.value" in cfg:
        print("passed, but should fail !!!")
    else:
        print("failed, as expected")
except Exception:
    print("failed (exception)")

print("example.py: check for config.sub.string variable availability is ", end="")
try:
    if "config.sub.string" in cfg:
        print("passed, as expected")
    else:
        print("failed, but should pass !!!")
except Exception:
    print("failed (exception)")

print("example.py: check for config.sub variable availability is ", end="")
try:
    if "config.sub" in cfg:
        print("passed, as expected")
    else:
        print("failed, but should pass !!!")
except Exception:
    print("failed (exception)")

print("example.py: === value query tests ===")
print(f"example.py: not selected for export, should return fallback (NOT_FOUND): cfg['config.value'] = {cfg.get('config.value', 'NOT_FOUND')}, type = {cfg.get_type('config.value')}")
print(f"example.py: not found in config, should return fallback (NOT_FOUND): cfg['config.empty'] = {cfg.get('config.empty', 'NOT_FOUND')}, type = {cfg.get_type('config.empty')}")
print(f"example.py: cfg['config.paths.tempdir'] = {cfg.get('config.paths.tempdir', 'NOT_FOUND')}, type = {cfg.get_type('config.paths.tempdir')}")
print(f"example.py: cfg['config.paths.workdir'] = {cfg.get('config.paths.workdir', 'NOT_FOUND')}, type = {cfg.get_type('config.paths.workdir')}")
print(f"example.py: cfg['config.paths.dynpath'] = {cfg.get('config.paths.dynpath', 'NOT_FOUND')}, type = {cfg.get_type('config.paths.dynpath')}")
print(f"example.py: cfg['config.paths.tempdir_raw'] = {cfg.get('config.paths.tempdir_raw', 'NOT_FOUND')}, type = {cfg.get_type('config.paths.tempdir_raw')}")
print(f"example.py: cfg['config.paths.workdir_raw'] = {cfg.get('config.paths.workdir_raw', 'NOT_FOUND')}, type = {cfg.get_type('config.paths.workdir_raw')}")
print(f"example.py: cfg['config.paths.dynpath_raw'] = {cfg.get('config.paths.dynpath_raw', 'NOT_FOUND')}, type = {cfg.get_type('config.paths.dynpath_raw')}")
print(f"example.py: cfg['config.sub.lua_v1'] = {cfg.get('config.sub.lua_v1', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.lua_v1')}")
print(f"example.py: cfg['config.sub.lua_v2'] = {cfg.get('config.sub.lua_v2', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.lua_v2')}")
print(f"example.py: cfg['config.sub.lua_v3'] = {cfg.get('config.sub.lua_v3', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.lua_v3')}")
print(f"example.py: cfg['config.sub.lua_num'] = {cfg.get('config.sub.lua_num', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.lua_num')}")
print(f"example.py: cfg['config.sub.extra_1'] = {cfg.get('config.sub.extra_1', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.extra_1')}")
print(f"example.py: cfg['config.sub.extra_2'] = {cfg.get('config.sub.extra_2', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.extra_2')}")
print(f"example.py: cfg['config.sub.number1'] = {cfg.get('config.sub.number1', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.number1')}")
print(f"example.py: cfg['config.sub.number2'] = {cfg.get('config.sub.number2', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.number2')}")
print(f"example.py: cfg['config.sub.string'] = {cfg.get('config.sub.string', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.string')}")
print(f"example.py: cfg['config.sub.problematic_string'] = {cfg.get('config.sub.problematic_string', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.problematic_string')}")
print(f"example.py: cfg['config.sub.non_latin_string'] = {cfg.get('config.sub.non_latin_string', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.non_latin_string')}")

# Test table access
print("example.py: === table tests for cfg['config.sub.sub'] ===")
print(f"example.py: cfg.is_table('config.sub.sub') = {cfg.is_table('config.sub.sub')}, type = {cfg.get_type('config.sub.sub')}")
print(f"example.py: table value should return fallback (NOT_FOUND): cfg['config.sub.sub'] = {cfg.get('config.sub.sub', 'NOT_FOUND')}")
print(f"example.py: table value as int should return fallback (-1): cfg['config.sub.sub'] = {cfg.get_int('config.sub.sub',-1)}")
print(f"example.py: table value as int should return fallback (-1.6 as int == -1): cfg['config.sub.sub'] = {cfg.get_int('config.sub.sub',-1.6)}")
print(f"example.py: table value as float should return fallback (-1.5): cfg['config.sub.sub'] = {cfg.get_float('config.sub.sub',-1.5)}")
print("example.py: === table's value tests for cfg['config.sub.sub'] ===")
print(f"example.py: cfg['config.sub.sub.message'] = {cfg.get('config.sub.sub.message', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.sub.message')}")
print(f"example.py: cfg['config.sub.sub.message2'] = {cfg.get('config.sub.sub.message2', 'NOT_FOUND')}, type = {cfg.get_type('config.sub.sub.message2')}")
print(f"example.py: cfg['config.sub.multiline_string'] = {cfg.get('config.sub.multiline_string', 'NOT_FOUND')}")

# Test empty table access
print("example.py: === empty table tests for cfg['config.sub.empty_table'] ===")
print(f"example.py: cfg.is_table('config.sub.empty_table') = {cfg.is_table('config.sub.empty_table')}, type = {cfg.get_type('config.sub.empty_table')}")
print(f"example.py: table value should return fallback (NOT_FOUND): cfg['config.sub.empty_table'] = {cfg.get('config.sub.empty_table', 'NOT_FOUND')}")
print(f"example.py: table start for cfg['config.sub.empty_table'] = {cfg.get_table_start('config.sub.empty_table')}")
print(f"example.py: table end for cfg['config.sub.empty_table'] = {cfg.get_table_end('config.sub.empty_table')}")

# Test mixed table access (indexed and named elements)
print("example.py: === mixed table tests for cfg['config.sub.mixed'] ===")
print(f"example.py: cfg.is_table('config.sub.mixed') = {cfg.is_table('config.sub.mixed')}, type = {cfg.get_type('config.sub.mixed')}")
print(f"example.py: table start for config.sub.mixed: {cfg.get_table_start('config.sub.mixed')}")
print(f"example.py: table end for config.sub.mixed: {cfg.get_table_end('config.sub.mixed')}")
print(f"example.py: table indices sequence for config.sub.mixed: {cfg.get_table_seq('config.sub.mixed')}")
print(f"example.py: cfg['config.sub.mixed.1'] = {cfg.get('config.sub.mixed.1', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.mixed.2'] = {cfg.get('config.sub.mixed.2', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.mixed.3'] = {cfg.get('config.sub.mixed.3', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.mixed.4'] = {cfg.get('config.sub.mixed.4', 'NOT_FOUND')}")
print(f"example.py: cfg['config.sub.mixed.key'] = {cfg.get('config.sub.mixed.key', 'NOT_FOUND')}")

# Show extra cmdline parameters passed to lua script as loader.args table and assigned to config.sub.loader_args
print("example.py: === test passing extra params (or cmdline args) into lua config ===")
print(f"example.py: config.sub.loader_args indices sequence: {cfg.get_table_seq('config.sub.loader_args')}")
for i in cfg.get_table_seq('config.sub.loader_args'):
    print(f"example.py: cfg['config.sub.loader_args.{i}'] = {cfg.get(f'config.sub.loader_args.{i}', 'NOT_FOUND')}")

# Test typed get
print("example.py: === test getting values with specific type from config.sub.types table ===")
print(f"example.py: get bool value, no fallback: cfg['config.sub.types.b'] = {cfg.get_bool('config.sub.types.b')}")
print(f"example.py: get missing bool value, fallback: cfg['config.sub.types.b1'] = {cfg.get_bool('config.sub.types.b1', False)}")
print(f"example.py: get bool value from int, fallback: cfg['config.sub.types.i'] = {cfg.get_bool('config.sub.types.i', False)}")

print(f"example.py: get int value, no fallback: cfg['config.sub.types.i'] = {cfg.get_int('config.sub.types.i')}")
print(f"example.py: get missing int value, fallback: cfg['config.sub.types.i1'] = {cfg.get_int('config.sub.types.i1', -1)}")
print(f"example.py: get missing int value, fallback from float num: cfg['config.sub.types.i1'] = {cfg.get_int('config.sub.types.i1', -2.6)}")
print(f"example.py: get int value from bool, fallback: cfg['config.sub.types.b'] = {cfg.get_int('config.sub.types.b', -1)}")

print(f"example.py: get float value, no fallback: cfg['config.sub.types.f'] = {cfg.get_float('config.sub.types.f')}")
print(f"example.py: get missing float value, fallback: cfg['config.sub.types.f1'] = {cfg.get_float('config.sub.types.f1', -1.1)}")
print(f"example.py: get float value from bool, fallback: cfg['config.sub.types.b'] = {cfg.get_float('config.sub.types.b', -1.1)}")

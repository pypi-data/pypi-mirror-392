from hatchling.builders.hooks.plugin.interface import BuildHookInterface

import os
import platform
import subprocess
import shutil
import hashlib


class CustomBuildHook(BuildHookInterface):
    def run(self, workdir, *cmd_args):
        """Run command in specified working directory and exit on failure"""
        result = subprocess.run(cmd_args, cwd=workdir)
        if result.returncode != 0:
            print(f"Command finished with exit code: {result.returncode}")
            raise subprocess.CalledProcessError(result.returncode, cmd_args)

    def check_sha256(self, file_path, checksum_file):
        """Check file checksum from sha256 checksum file"""
        print(f"Loading checksum file: {checksum_file}")
        # Read the expected checksum from the checksum file
        with open(checksum_file, "r") as f:
            checksum_line = f.read().strip()
        # Parse the checksum and filename from the line
        # Format: "checksum *filename" or "checksum filename"
        parts = checksum_line.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid checksum file format: {checksum_line}")
        expected_checksum = parts[0]
        expected_filename = parts[1].lstrip("*")  # Remove leading '*' if present
        # Verify the filename matches
        actual_filename = os.path.basename(file_path)
        if expected_filename != actual_filename:
            raise ValueError(
                f"Filename mismatch: expected '{expected_filename}', got '{actual_filename}'"
            )
        # Calculate the actual checksum
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        actual_checksum = sha256_hash.hexdigest()
        # Compare checksums
        if actual_checksum != expected_checksum:
            raise ValueError(
                f"Checksum mismatch for {file_path}: expected {expected_checksum}, got {actual_checksum}"
            )
        print(f"Checksum verified: {file_path}")
        return True

    def initialize(self, version, build_data):
        build_data["pure_python"] = False
        build_data["infer_tag"] = True
        # Get needed params
        current_os = platform.system().lower()
        arch = platform.machine().lower()
        print(f"OS: {current_os}, arch: {arch}")
        # Lua build defines
        lua_version = "5.4.8"
        lua_src = f"lua-{lua_version}.tar.gz"
        lua_checksum = f"lua-{lua_version}.sha256"
        lua_patch = "build.patch"
        # Define paths
        root_dir = os.path.dirname(__file__)
        lua_dir = os.path.join(root_dir, "lua")
        package_dir = os.path.join(root_dir, "python_lua_helper")
        base_build_dir = os.path.join(lua_dir, "build")
        lua_build_dir = os.path.join(base_build_dir, f"lua-{lua_version}")
        if current_os == "linux":
            print("Linux detected - building Lua from source...")
            # Clean/create main build directory
            if os.path.exists(base_build_dir):
                shutil.rmtree(base_build_dir)
            os.makedirs(base_build_dir, exist_ok=False)
            # Download Lua source if it doesn't exist
            if not os.path.exists(os.path.join(lua_dir, lua_src)):
                print(f"Downloading {lua_src}")
                self.run(
                    lua_dir,
                    "curl",
                    "-s",
                    "-L",
                    "-o",
                    lua_src,
                    f"https://www.lua.org/ftp/{lua_src}",
                )
            # Check checksum
            print(f"Checking {lua_src}")
            self.check_sha256(
                os.path.join(lua_dir, lua_src),
                os.path.join(lua_dir, lua_checksum),
            )
            # Extract archive
            shutil.unpack_archive(os.path.join(lua_dir, lua_src), base_build_dir)
            # Apply patch
            print("Applying build patch...")
            self.run(
                lua_build_dir,
                "patch",
                "-p1",
                "-i",
                os.path.join(lua_dir, lua_patch),
            )
            # Build Lua with optimization flags
            print("Building Lua...")
            self.run(
                lua_build_dir,
                "make",
                "PLAT=linux",
                "MYCFLAGS=-Os -fPIE -flto=auto -fuse-linker-plugin -ffat-lto-objects",
                "MYLDFLAGS=-Os -pie -static -flto=auto -fuse-linker-plugin -ffat-lto-objects -Wl,-z,relro,-z,now",
            )
            # Strip binary
            print("Stripping Lua binary...")
            lua_binary = os.path.join(lua_build_dir, "src", "lua")
            self.run(lua_build_dir, "strip", "--strip-unneeded", lua_binary)
            # Copy result
            print("Copying Lua binary...")
            target_binary = os.path.join(package_dir, "lua")
            shutil.copy2(lua_binary, target_binary)
        elif current_os == "windows":
            print(
                f"Windows detected (architecture: {arch}) - selecting pre-built Lua binary..."
            )
            target_binary = os.path.join(package_dir, "lua.exe")
            if arch in ["x86_64", "amd64"]:
                source_binary = os.path.join(lua_dir, "lua-windows-x86_64")
            elif arch in ["i386", "i586", "i686", "x86"]:
                source_binary = os.path.join(lua_dir, "lua-windows-i686")
            else:
                print(
                    f"Warning: Unsupported Windows architecture '{arch}' - no Lua binary available"
                )
                return
            shutil.copy2(source_binary, target_binary)
            print(f"Copied {source_binary} to {target_binary}")
        else:
            print(
                f"Warning: Unsupported operating system '{current_os}' - no Lua binary available"
            )

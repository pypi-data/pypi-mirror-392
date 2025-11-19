set -e

compiler="$1"
arch="$2"

[[ -z $compiler ]] && echo "compiler prefix must be provided" && exit 1
[[ -z $arch ]] && echo "arch name must be provided" && exit 1

script_dir="$(cd "$(dirname "$0")" && pwd)"

lua_version="5.4.8"
lua_src="lua-$lua_version.tar.gz"
lua_checksum="lua-$lua_version.sha256"

cd "$script_dir"

[[ ! -e "$lua_src" ]] && echo "downloading $lua_src" && curl -s -L -o "$script_dir/$lua_src" "https://www.lua.org/ftp/$lua_src"
echo "checking $lua_src" && sha256sum -c "$lua_checksum"

rm -rf "$script_dir/build"
mkdir -p "$script_dir/build"

cd "$script_dir/build"
tar xf "$script_dir/$lua_src"

cd "$script_dir/build/lua-$lua_version"
patch -p1 -i "$script_dir/build.patch"
make \
  PLAT=mingw \
  CC="$compiler-gcc -std=gnu99" \
  AR="$compiler-ar rc" \
  RANLIB="$compiler-ranlib" \
  MYCFLAGS="-Os -fPIE -flto=auto -fuse-linker-plugin -ffat-lto-objects" \
  MYLDFLAGS="-Os -pie -static -flto=auto -fuse-linker-plugin -ffat-lto-objects"

$compiler-strip --strip-unneeded src/lua.exe
cp -v src/lua.exe "$script_dir/lua-windows-$arch"

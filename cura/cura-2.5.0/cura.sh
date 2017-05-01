#! /bin/bash
#
# Cura-2.5.AppImage from
# https://ultimaker.com/en/products/cura-software
# fails with relative paths.
#
# Here is the workaround.
# save this shell script under the name cura in the same
# directory, where Cura-2.5.AppImage is and make both
# executable.
#
# (C) juergen@fabmail.org
#
args=()
for arg in "$@"; do
	case $arg in
		# keep options and absolute paths as is.
		-* | /* )
			;;
		# make relative paths absolute.
		* ) arg=$(pwd)/$arg
			;;
	esac
	# append to array.
	args+=("$arg")
done
exec $(dirname "$0")/Cura-2.5.0.AppImage "${args[@]}"

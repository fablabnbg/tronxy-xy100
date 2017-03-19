#! /bin/sh
DAYS=6
dst=HOME.local/share/cura
src=$HOME/.local/share/cura
files=$(cd /home/jw/.local/share/cura; find * -type f -a -ctime -$DAYS | grep -v '^cura.log$')
for f in $files; do
  mkdir -p $dst/$(dirname $f)
  cp $src/$f $dst/$f
  echo git add $dst/$f
  git add $dst/$f
done

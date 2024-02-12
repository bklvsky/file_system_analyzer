chmod 000 forbidden.txt

# creating symlink loop
mkdir dir1
mkdir dir2

cd dir1
ln -s ../dir2 ./link_dir2

cd ../dir2
ln -s ../dir1/link_dir2 ./link_link1


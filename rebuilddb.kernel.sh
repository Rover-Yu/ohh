#! /bin/sh

set -x

rm -f *cscope*
rm -f *tags*

find arch/x86/ block/ crypto/ init/ ipc/ kernel/ lib/ mm virt/ -name "*.[chS]">> cscope.files
find drivers/ -name "*.[chS]" | grep -E -e '(/acpi/)|(/base/)|(/block/)|(ers/char/)|(clocksource/)|(dma/)|(/net/.*/igb/)|(/pci/)|(net/[^/]+.c)' >> cscope.files
find fs/ -name "*.[chS]" | grep -E -e "(btrfs)|(fs/configfs/)|(fs/debugfs/)|(/ext[234]/)|(hugetlbfs)|(notify)|(fs/proc)|(/sysfs)|(cachefs)" >> cscope.files 
find include/ -name "*.[chS]" >> cscope.files
find net/ -name "*.[chS]" | grep -E -e "(^net/core)|(^net/sched)|(^net/ethernet)|(^net/ipv4)|(^net/unix)|(^net/netfilter)|(^net/netlink)|(^net/bridge)" >> cscope.files 
ls net/*.c >> cscope.files 
ls net/*.h >> cscope.files
ls fs/*.c >> cscope.files 
ls fs/*.h >> cscope.files

ctags --excmd=number --fields=afiKlmnSzt -L cscope.files

echo "-k" > cscope.files.cs
echo "-q" >> cscope.files.cs
cat cscope.files >> cscope.files.cs
mv cscope.files.cs cscope.files
cscope -b -k -q
#cscope -q -L -1 do_timer


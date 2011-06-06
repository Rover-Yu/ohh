#! /bin/sh -x


blacklist="(sparc)|(arm)|(microblaze)|(powerpc)|(ppc)|(s390)|(mips)|(cris)|(m68k)|(alpha)|(bsd-user)|(darwin-user)|(linux-user)|(ppc)|(sh4)|(ia64)|(tests)|(kvm/)|(kvm-stub.c)|(win32)"

find -name "*.newkvm.*"	-exec rm -f {} \;

rm -f cscope.files
touch cscope.files
unifdef_list=""
for fn in `grep CONFIG_USER_ONLY  * -rn | cut -d : -f 1 | sort | uniq | grep "\.[chSs]$"`; do
	unifdef_list="${unifdef_list}|(${fn})"
	echo "${fn}.newkvm" >> cscope.files
	unifdef -U CONFIG_USER_ONLY $fn > $fn.newkvm;
done

for fn in `grep OBSOLETE_KVM_IMPL  * -rn | cut -d : -f 1 | sort | uniq | grep "\.[chSs]$"`; do
	unifdef_list="${unifdef_list}|(${fn})"
	echo "${fn}.newkvm" >> cscope.files
	unifdef -U OBSOLETE_KVM_IMPL $fn > $fn.newkvm;
done

find -name "*.[chsS]" | grep -v -E "${blacklist}|${unifdef_list}" >> cscope.files

cscope -b -q
ctags --excmd=number --fields=afiKlmnSzt -L cscope.files

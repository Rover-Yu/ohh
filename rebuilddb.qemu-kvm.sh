#! /bin/sh


blacklist="(sparc)|(arm)|(microblaze)|(powerpc)|(ppc)|(s390)|(mips)|(cris)|(m68k)|(alpha)|(bsd-user)|(darwin-user)|(linux-user)|(ppc)|(sh4)|(ia64)|(tests)|(kvm/)|(kvm-stub.c)|(win32)"

find -name "*.newkvm.*"	-exec rm -f {} \;

rm -f cscope.files
touch cscope.files
unifdef_list=""
for fn in `grep CONFIG_USER_ONLY  * -rn | grep -v -E "${blacklist}" | cut -d : -f 1 | sort | uniq | grep "\.[chSs]$"`; do
	unifdef_list="${unifdef_list}|(${fn})"
	newkvm_c="${fn}.newkvm.c"
	echo "${newkvm_c}" >> cscope.files
	unifdef -U CONFIG_USER_ONLY $fn > ${newkvm_c}	;
done

for fn in `grep OBSOLETE_KVM_IMPL  * -rn | grep -v -E "${blacklist}" | cut -d : -f 1 | sort | uniq | grep "\.[chSs]$"`; do
	unifdef_list="${unifdef_list}|(${fn})"
	newkvm_c="${fn}.newkvm.c"
	echo "${newkvm_c}" >> cscope.files
	unifdef -U OBSOLETE_KVM_IMPL $fn > ${newkvm_c}	;
done

set -x
find -name "*.[chsS]" | grep -v -E "${blacklist}${unifdef_list}" >> cscope.files
set +x

cscope -b -q
ctags --excmd=number --fields=afiKlmnSzt -L cscope.files

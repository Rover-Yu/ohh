#! /bin/sh

find -name "*.[chsS]" | grep -v -E  "(sparc)|(arm)|(microblaze)|(powerpc)|(ppc)|(s390)|(mips)|(cris)|(m68k)|(alpha)|(bsd-user)|(darwin-user)|(linux-user)|(ppc)|(sh4)|(ia64)|(tests)|(target-i386/kvm.c)|(cpus.c)|(kvm-all.c)|(kvm.h)|(kvm/)|(kvm-stub.c)|(win32)" > cscope.files

unifdef -U OBSOLETE_KVM_IMPL target-i386/kvm.c > target-i386/kvm.c.newkvm.c
unifdef -U OBSOLETE_KVM_IMPL cpus.c > cpus.c.newkvm.c
unifdef -U OBSOLETE_KVM_IMPL kvm-all.c > kvm-all.c.newkvm.c
unifdef -U OBSOLETE_KVM_IMPL kvm.h  > kvm.h.newkvm.h

echo "./target-i386/kvm.c.newkvm.c" >> cscope.files
echo "./cpus.c.newkvm.c" >> cscope.files
echo "./kvm-all.c.newkvm.c" >> cscope.files
echo "./kvm.h.newkvm.h" >> cscope.files

cscope -b -q
ctags --excmd=number --fields=afiKlmnSzt -L cscope.files

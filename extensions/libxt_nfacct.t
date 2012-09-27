:INPUT,FORWARD,OUTPUT
!nfacct add test
#
# extra space in iptables-save output, fix it
#
-m nfacct --nfacct-name test;=;OK
-m nfacct --nfacct-name wrong;;FAIL
-m nfacct;;FAIL
!nfacct del test

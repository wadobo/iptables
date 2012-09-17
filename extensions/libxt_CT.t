:PREROUTING,OUTPUT
*raw
-j CT --notrack;=;OK
-j CT --ctevents new,related,destroy,reply,assured,protoinfo,helper,mark;=;OK
-j CT --expevents new;=;OK
-j CT --zone 0;=;OK
-j CT --zone 65535;=;OK
-j CT --zone 65536;;FAIL
-j CT --zone -1;;FAIL
-j CT;;FAIL
!nfct timeout add test inet tcp ESTABLISHED 100
-j CT --timeout test;=;OK
!nfct timeout del test
!nfct helper add rpc inet tcp
-j CT --helper rpc;=;OK
!nfct helper del rpc

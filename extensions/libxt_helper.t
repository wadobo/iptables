:INPUT,FORWARD,OUTPUT
-m helper --helper ftp;=;OK
# should be OK?
-m helper --helper wrong;;FAIL
-m helper;;FAIL

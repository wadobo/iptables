:FORWARD,OUTPUT,POSTROUTING
*mangle
-j CLASSIFY --set-class 0000:ffff;=;OK
# maximum handle accepted by tc is 0xffff
-j CLASSIFY --set-class 0000:ffffffff;;FAIL
-j CLASSIFY --set-class 1:-1;;FAIL
-j CLASSIFY;;FAIL

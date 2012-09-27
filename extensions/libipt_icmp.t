:INPUT,FORWARD,OUTPUT
-p icmp -m icmp --icmp-type any;=;OK
# output uses the number, better use the name?
-p icmp -m icmp --icmp-type echo-reply;=;OK
# output uses the number, better use the name?
-p icmp -m icmp --icmp-type destination-unreachable;=;OK
# it does not acccept name/name, should we accept this?
-p icmp -m icmp --icmp-type destination-unreachable/network-unreachable;=;OK
-m icmp;;FAIL
# we accept "iptables -I INPUT -p tcp -m tcp", why not this below?
-p icmp -m icmp;=;OK

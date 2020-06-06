---
title: "TCPReplay"
date: 2020-06-06T14:00:30+02:00
cover: "/img/wireshark-tcp-replay/wireshark.png" 
---
# Wireshark and TCPReplay

Wireshark is a useful tool to that we often use at Captain AI to monitor network traffic on a vessel. It can be useful to see at a very fine grained level what packets are being sent, and to whom. It's not even necessarily always packets meant for you, which is why it's also a tool sometimes employed by techies of a more eh dubious nature. Wireshark also has the ability to sniff out packets that you would not usually detect in code because it didn't manage to get past the firewall, the MAC address was incorrect, or for any other reason. Usually, Wireshark will still show it, which I find quite amazing, and very useful. It's kind of the final lithmus test of networking, if Wireshark doesn't see it, it's probably really not there. 

When you start a Wireshark session by clicking the shark-finned play button (see what they did there?!), it will collect all the data according to your filters. I am not going to dive into how all this works, there's plenty of good resources for that on the internet. What I did want to discuss quickly is how to replay this information. Capturing is one thing, but it is often interesting to replay that data back into a network, often not quite the same network as before. This means the IP addresses and the MAC addresses need to be rewritten. Enter the tcprewrite tool.

## TCPRewrite

TCPRewrite can be used to modify pcap files and is part of the tcpreplay suite. Install it on Ubuntu using `apt-get install tcprewrite` or on Mac using `brew install tcpreplay`. For us and I think for many folks the use case is that you simply want to replay your pcap data back to yourself, so that regardless of the original target IP address it should now be set to your own IP. Usually you would want to use the loopback device for this, but I had trouble getting that to work (Wireshark would show those packets then as N/A) so I resorted to using my regular network interface for this. After some toying around with ifconfig I found my IP address and issued a rewrite like this:

```
tcprewrite --infile file.pcap --outfile file-2.pcap --dstipmap '0.0.0.0/0:192.168.9.5' --srcipmap '0.0.0.0/0:192.168.9.5'
```

You can find your IP address with `ifconfig` on Mac and Linux. It will usually output quite a few interfaces. Docker might have one, your ethernet, wireless, VPN etc. Just find the one you want to play back on, often the one that actually has an `inet` address set. The `ether` part denotes the MAC address. Ignore inet6, that's your IPv6 address. Like that is ever gonna happen anymore!

**NOTE Make sure you don't use the same out file as the infile, it will not work and corrupt your file!** The interesting parameters here are the IP maps, these key value pairs map old addresses to new ones. They should be CIDR format, so you can use a group, in this case the `0.0.0.0/0` simply says all of the IP addresses, i.e. its kind of a wildcard. SO that worked, except that when I replayed it and used netcat or so it didn't work. When I opened Wireshark yet again I did see the packets coming in and gave me an idea of why they were not formally accepted. The MAC addresses were still set to the old MAC addresses. Your network interface will probably be a bit iffy about those packets that say they are addressed to them but then have the wrong MAC address. So we also have to rewrite the MAC addresses. So including the IP stuff the command becomes

```bash
tcprewrite --infile file.pcap --outfile file-2.pcap --dstipmap '0.0.0.0/0:192.168.9.5' --srcipmap '0.0.0.0/0:192.168.9.5' --enet-smac <YOUR_MAC> --enet-dmac <YOUR_MAC>'
```

That should work. In my case though I also needed to rewrite some ports. Simple as pie, you just add the `portmap` param:

```bash
tcprewrite --infile file.pcap --outfile file-2.pcap --dstipmap '0.0.0.0/0:192.168.9.5' --srcipmap '0.0.0.0/0:192.168.9.5' --enet-smac f0:18:98:9f:91:57 --enet-dmac f0:18:98:9f:91:57 --portmap 3000-4000:7777
```

Because figuring out your MAC addresses and IP addresses is a hassle I wrote a small shell script for it that will rewrite the file for you based on the interface you give it and the pcap file.

```bash
#!/bin/bash
# Automatically rewrite a pcap file according to your IP address and MAC
# Arg 1 should be the pcap file to rewrite in place
# Arg 2 the interface you want to use (loopback or eth or ...)

set -xe 
if [ -z "$1" ]
  then
    echo "No pcap file specified"
    exit
fi
if [ -z "$2" ]
  then
    echo "No interface argument specified"
    exit
fi

TEMP='/tmp/rewrite-temp.pcap'
IP=`ifconfig $2 | grep 'inet ' | cut -d' ' -f2`
if [ -z "$IP" ]
  then
    echo "No IP address found for interface $2"
    exit
fi

MAC=`ifconfig $2 | grep 'ether ' | cut -d' ' -f2`
if [ -z "$MAC" ]
  then
    echo "No MAC address found for interface $2"
    exit
fi
tcprewrite --infile $1 --outfile $TEMP --dstipmap 0.0.0.0/0:$IP --srcipmap 0.0.0.0/0:$IP --enet-smac $MAC --enet-dmac $MAC
rm $TEMP # Clean up

```

This interface will usually not change so it's more convenient than using IP and MAC addresses. I would run this on my Mac like so: 

```bash
sh tcp_rewrite.sh file.pcap en0
```

Change the interface according to your config. That should do it as far as the rewrite is concerned.

## TCPReplay

Given the rewritten pcap file we can replay this data to our own machine close to how it was originally recorded using [tcpreplay](http://tcpreplay.appneta.com/). The only required arguments are the interface (`-i`) and the pcap file, although I find it useful to include `-K` which preloads the pcap into memory boosting performance at the cost of RAM and `--stats 1` which gives a nice summary of metrics like throughput every second. You can also add `-t` to just ignore the timestamps and play it back as fast as possible (this can be a good stress test for your networking application!). Alternatively you can use `-x <multiplier>` to modify playback where the multiplier will accelerate (or decellerate for values < 1) the original playback speed by a constant factor.

Putting it all together you might have something like

`tcpreplay -i en0 -x 10 --stats=1 file.pcap`

To play back the pcap file at 10x speed over interface `en0`. As with everything in life if it doesnt work the first time, use `sudo`. Just kidding, please careful with that in general, but here it might be warranted in order to get access to the interface.

That's it. Let me know if you need any help with anything!



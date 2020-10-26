```
        ███╗   ███╗███╗   ██╗███████╗
        ████╗ ████║████╗  ██║██╔════╝
        ██╔████╔██║██╔██╗ ██║███████╗
        ██║╚██╔╝██║██║╚██╗██║╚════██║
        ██║ ╚═╝ ██║██║ ╚████║███████║
        ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝            

        # Monitor New Subdomain
        # @omarelfarsaoui
        # 1.0     
```
# monitor-new-subdomain


## Requirements
 * python3 
 * vps (aws free account is enough) *[Create aws account ](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)*
 * Slack workspace (Free) *[Create Slack Webhook URL](https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack)*
 * Telegram *[Create Telegram bot](https://medium.com/@xabaras/sending-a-message-to-a-telegram-channel-the-easy-way-eb0a0b32968)*

### Intallation

MNS needs some dependencies, to install them on your 

```
$ git clone 
$ cd monitor-new-subdomain/
$ pip3 install -r requirements.txt

```

### Usage

** add domain to monitor. E.g: domain.com
```
python3 check-new-subdomain.py -a 
```

** list all domain in database
```
python3 check-new-subdomain.py -l
```

** get all subdomain for specific domain
```
python3 check-new-subdomain.py -L domain.com
```

** search fo new subdomain for all domains
```
python3 check-new-subdomain.py -m
```

** delete domain
```
python3 check-new-subdomain.py -d
```

** send notification via slack 
```
python3 check-new-subdomain.py -s
```

** send notification via telegram 
```
python3 check-new-subdomain.py -t
```



### Todo
 * add Docker
 * add more subdomain resources
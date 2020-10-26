```
                        ███╗   ███╗███╗   ██╗███████╗
                        ████╗ ████║████╗  ██║██╔════╝
                        ██╔████╔██║██╔██╗ ██║███████╗
                        ██║╚██╔╝██║██║╚██╗██║╚════██║
                        ██║ ╚═╝ ██║██║ ╚████║███████║
                        ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝            

                        # Monitor New Subdomain
                        # @omarelfarsaoui
                        # version 1.0     
```
# monitor-new-subdomain


## Requirements
 * python3 
 * MongoDB *[how to install mongodb](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-18-04)*
 * vps (aws free account is enough) *[Create aws account ](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)*
 * Slack workspace (Free) *[Create Slack Webhook URL](https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack)*
 * Telegram bot *[Create Telegram bot](https://medium.com/@xabaras/sending-a-message-to-a-telegram-channel-the-easy-way-eb0a0b32968)*

### Intallation

MNS needs some dependencies, to install them on your 

```
$ git clone https://github.com/elfarsaouiomar/monitor-new-subdomain.git
$ cd monitor-new-subdomain/
$ pip3 install -r requirements.txt

```

### Usage

**add domain to monitor. E.g: domain.com**
```
python3 check-new-subdomain.py -a 
```

**list all domain in database**
```
python3 check-new-subdomain.py -l
```

**get all subdomain for specific domain**
```
python3 check-new-subdomain.py -L domain.com
```

**search fo new subdomain for all domains**
```
python3 check-new-subdomain.py -m
```

**delete domain**
```
python3 check-new-subdomain.py -d
```

**send notification via slack**
```
python3 check-new-subdomain.py -s
```

**send notification via telegram**
```
python3 check-new-subdomain.py -t
```

## example

**list all domains**

![subdomain monitor](https://i.ibb.co/6ZNWtJS/Screenshot-from-2020-10-26-14-27-24.png)


**monitor new subdomain**

![subdomain monitor](https://i.ibb.co/TYN3hRg/Screenshot-from-2020-10-26-15-00-34.png)

**mongoDB result**

![subdomain monitor](https://i.ibb.co/CKL3Hw0/target.png)


**notification telegram**

![subdomain monitor](https://i.ibb.co/L8shfJG/Screenshot-from-2020-10-26-15-02-13.png)


### Todo
 * add Docker
 * add more subdomain resources

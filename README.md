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
 * Slack workspace (Free) *[Create Slack Webhook URL](https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack)* (optional)
 * Telegram bot *[Create Telegram bot](https://medium.com/@xabaras/sending-a-message-to-a-telegram-channel-the-easy-way-eb0a0b32968)* (optional)

### Intallation

MNS needs some dependencies, to install them on your 

```bash
$ git clone https://github.com/elfarsaouiomar/monitor-new-subdomain.git
$ cd monitor-new-subdomain/
$ pip3 install -r requirements.txt

```

### Usage

**add domain to monitor. E.g: domain.com**
```bash
python3 check-new-subdomain.py -a  domain.com
```

**list all domain in database**
```bash
python3 check-new-subdomain.py -l
```

**get all subdomain for specific domain**
```
python3 check-new-subdomain.py -L domain.com
```

**search fo new subdomain for all domains**
```bash
python3 check-new-subdomain.py -m
```
**export all subdomains form the database to txt file**
```bash
python3 check-new-subdomain.py -e filename
```

**import list of domains via file**

_each domain in line_
```bash
python3 check-new-subdomain.py -i domains.txt
```

**delete domain**
```
python3 check-new-subdomain.py -d
```

**send notification via slack**
```bash
python3 check-new-subdomain.py -s
```

**send notification via telegram**
```bash
python3 check-new-subdomain.py -t
```

## example

**list all domains**

![subdomain monitor](https://i.ibb.co/6ZNWtJS/Screenshot-from-2020-10-26-14-27-24.png)


**monitor new subdomain**

![subdomain monitor](https://i.ibb.co/TYN3hRg/Screenshot-from-2020-10-26-15-00-34.png)


**Import domains via file**

![import domains](https://i.ibb.co/HzwxgC7/import.jpg)


**mongoDB result**

![subdomain monitor](https://i.ibb.co/CKL3Hw0/target.png)


**notification telegram**

![subdomain monitor](https://i.ibb.co/L8shfJG/Screenshot-from-2020-10-26-15-02-13.png)


## Feedback and issues
***[Create a new release](https://github.com/elfarsaouiomar/monitor-new-subdomain/releases/new)***

## inspired from https://github.com/yassineaboukir/sublert

### Todo
 * add output file
 * add Docker
 * add more subdomain resources
    * Certspotter
    * Virustotal
    * ~~Sublist3r~~
    * Facebook **
    * Spyse (CertDB) *
    * Bufferover
    * Threatcrowd
    * Virustotal with apikey **
    * AnubisDB
    * Urlscan.io
    * SecurityTrails **
    * Threatminer

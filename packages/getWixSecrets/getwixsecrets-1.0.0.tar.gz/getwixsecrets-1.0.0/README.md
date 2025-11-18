# getSecrets package

getWIXSecrets is a simple package that reads from a WIX site secrets vault
It can also read data from the local vault.yml file

usage:

```
from getSecrets import *

data = get_secret(<id>)

usr, pwd = get_user_pwd(<id> )

updater = update_secret(<id>, <new_object>)

```

Vault parameters are stored in a config file ~/.config/.vault/.vault.yml

```
WIXAPI:
  token: "<access token>"
  url: https://wwww.mysite.com
  uri: _functions/secrets
 
id:
  item1: 1
  item2: 2
  username: user
  password: !@•?
```


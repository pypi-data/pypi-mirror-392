"""
Default configuration file for LiveChat Webservice
"""


class Config:
    LIVECHAT_BASE_URL = "https://api.livechatinc.com/v3.6"
    MAX_CONNECTIONS = 5 # TODO actually see what's a good number here
    MAX_KEEPALIVE_CONNECTIONS = 5
    KEEPALIVE_EXPIRY = 30.0
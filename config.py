"""
规则来源：
https://github.com/kelvinBen/AppInfoScanner
https://github.com/GerbenJavado/LinkFinder
"""


url_reg_list = [
    r'/https:\/\/[a-zA-Z0-9\/.?=%&]*|http:\/\/[a-zA-Z0-9\/.?=%&]*/gm',
    r'.*://([\d{1,3}\.]{3}\d{1,3}).*',
    r'src=[\'"].*?[\'"]',
    r'href=[\'"].*?[\'"]',
    r'<script [^><]*?src=[\'"].*?[\'"]'
]


LinkFinder_reg = r"""
    (?:"|')                               # Start newline delimiter
    (
    ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
    [^"'/]{1,}\.                        # Match a domainname (any character + dot)
    [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
    |
    ((?:/|\.\./|\./)                    # Start with /,../,./
    [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
    [^"'><,;|()]{1,})                   # Rest of the characters can't be
    |
    ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
    [a-zA-Z0-9_\-/]{1,}                 # Resource name
    \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
    (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
    |
    ([a-zA-Z0-9_\-]{1,}                 # filename
    \.(?:php|asp|aspx|jsp|json|
            action|html|js|txt|xml)             # . + extension
    (?:\?[^"|']{0,}|))                  # ? mark with parameters
    )
    (?:"|')                               # End newline delimiter
"""


ak_reg_list = {
    "Aliyun_OSS": [
        r'.*accessKeyId.*".*?"',
        r'.*accessKeySecret.*".*?"',
        r'.*secret.*".*?"'
    ],
    "Amazon_AWS_Access_Key_ID": r"([^A-Z0-9]|^)(AKIA|A3T|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{12,}",
    "Amazon_AWS_S3_Bucket": [
    	r"//s3-[a-z0-9-]+\\.amazonaws\\.com/[a-z0-9._-]+",
    	r"//s3\\.amazonaws\\.com/[a-z0-9._-]+",
    	r"[a-z0-9.-]+\\.s3-[a-z0-9-]\\.amazonaws\\.com",
    	r"[a-z0-9.-]+\\.s3-website[.-](eu|ap|us|ca|sa|cn)",
    	r"[a-z0-9.-]+\\.s3\\.amazonaws\\.com",
    	r"amzn\\.mws\\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    ],
    "Artifactory_API_Token": r"(?:\\s|=|:|\"|^)AKC[a-zA-Z0-9]{10,}",
    "Artifactory_Password": r"(?:\\s|=|:|\"|^)AP[\\dABCDEF][a-zA-Z0-9]{8,}",
    "Authorization_Basic": r"basic\\s[a-zA-Z0-9_\\-:\\.=]+",
    "Authorization_Bearer": r"bearer\\s[a-zA-Z0-9_\\-:\\.=]+",
    "AWS_API_Key": r"AKIA[0-9A-Z]{16}",
    "Basic_Auth_Credentials": r"(?<=:\/\/)[a-zA-Z0-9]+:[a-zA-Z0-9]+@[a-zA-Z0-9]+\\.[a-zA-Z]+",
    "Cloudinary_Basic_Auth": r"cloudinary:\/\/[0-9]{15}:[0-9A-Za-z]+@[a-z]+",
    "DEFCON_CTF_Flag": r"O{3}\\{.*\\}",
    "Discord_BOT_Token": r"((?:N|M|O)[a-zA-Z0-9]{23}\\.[a-zA-Z0-9-_]{6}\\.[a-zA-Z0-9-_]{27})$",
    "Facebook_Access_Token": r"EAACEdEose0cBA[0-9A-Za-z]+",
    "Facebook_ClientID": r"[f|F][a|A][c|C][e|E][b|B][o|O][o|O][k|K](.{0,20})?['\"][0-9]{13,17}",
    "Facebook_OAuth": r"[f|F][a|A][c|C][e|E][b|B][o|O][o|O][k|K].*['|\"][0-9a-f]{32}['|\"]",
    "Facebook_Secret_Key": r"([f|F][a|A][c|C][e|E][b|B][o|O][o|O][k|K]|[f|F][b|B])(.{0,20})?['\"][0-9a-f]{32}",
    "Firebase": r"[a-z0-9.-]+\\.firebaseio\\.com",
    "Generic_API_Key": r"[a|A][p|P][i|I][_]?[k|K][e|E][y|Y].*['|\"][0-9a-zA-Z]{32,45}['|\"]",
    "Generic_Secret": r"[s|S][e|E][c|C][r|R][e|E][t|T].*['|\"][0-9a-zA-Z]{32,45}['|\"]",
    "GitHub": r"[g|G][i|I][t|T][h|H][u|U][b|B].*['|\"][0-9a-zA-Z]{35,40}['|\"]",
    "GitHub_Access_Token": r"([a-zA-Z0-9_-]*:[a-zA-Z0-9_-]+@github.com*)$",
    "Google_API_Key": r"AIza[0-9A-Za-z\\-_]{35}",
    "Google_Cloud_Platform_OAuth": r"[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
    "Google_Cloud_Platform_Service_Account": r"\"type\": \"service_account\"",
    "Google_OAuth_Access_Token": r"ya29\\.[0-9A-Za-z\\-_]+",
    "HackerOne_CTF_Flag": r"[h|H]1(?:[c|C][t|T][f|F])?\\{.*\\}",
    "HackTheBox_CTF_Flag": r"[h|H](?:[a|A][c|C][k|K][t|T][h|H][e|E][b|B][o|O][x|X]|[t|T][b|B])\\{.*\\}$",
    "Heroku_API_Key": r"[h|H][e|E][r|R][o|O][k|K][u|U].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
    "IP_Address": r"(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])",
    "JSON_Web_Token": r"(?i)^((?=.*[a-z])(?=.*[0-9])(?:[a-z0-9_=]+\\.){2}(?:[a-z0-9_\\-\\+\/=]*))$",
    "LinkFinder": r"(?:\"|')(((?:[a-zA-Z]{1,10}:\/\/|\/\/)[^\"'\/]{1,}\\.[a-zA-Z]{2,}[^\"']{0,})|((?:\/|\\.\\.\/|\\.\/)[^\"'><,;| *()(%%$^\/\\\\\\[\\]][^\"'><,;|()]{1,})|([a-zA-Z0-9_\\-\/]{1,}\/[a-zA-Z0-9_\\-\/]{1,}\\.(?:[a-zA-Z]{1,4}|action)(?:[\\?|#][^\"|']{0,}|))|([a-zA-Z0-9_\\-\/]{1,}\/[a-zA-Z0-9_\\-\/]{3,}(?:[\\?|#][^\"|']{0,}|))|([a-zA-Z0-9_\\-]{1,}\\.(?:php|asp|aspx|jsp|json|action|html|js|txt|xml)(?:[\\?|#][^\"|']{0,}|)))(?:\"|')",
    "Mac_Address": r"(([0-9A-Fa-f]{2}[:]){5}[0-9A-Fa-f]{2}|([0-9A-Fa-f]{2}[-]){5}[0-9A-Fa-f]{2}|([0-9A-Fa-f]{4}[\\.]){2}[0-9A-Fa-f]{4})$",
    "MailChimp_API_Key": r"[0-9a-f]{32}-us[0-9]{1,2}",
    "Mailgun_API_Key": r"key-[0-9a-zA-Z]{32}",
    "Mailto": r"(?<=mailto:)[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9.-]+",
    "Password_in_URL": r"[a-zA-Z]{3,10}://[^/\\s:@]{3,20}:[^/\\s:@]{3,20}@.{1,100}[\"'\\s]",
    "PayPal_Braintree_Access_Token": r"access_token\\$production\\$[0-9a-z]{16}\\$[0-9a-f]{32}",
    "PGP_private_key_block": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
    "Picatic_API_Key": r"sk_live_[0-9a-z]{32}",
    "RSA_Private_Key": r"-----BEGIN RSA PRIVATE KEY-----",
    "Slack_Token": r"(xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32})",
    "Slack_Webhook": r"https://hooks.slack.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}",
    "Square_Access_Token": r"sq0atp-[0-9A-Za-z\\-_]{22}",
    "Square_OAuth_Secret": r"sq0csp-[0-9A-Za-z\\-_]{43}",
    "SSH_DSA_Private_Key": r"-----BEGIN DSA PRIVATE KEY-----",
    "SSH_EC_Private_Key": r"-----BEGIN EC PRIVATE KEY-----",
    "Stripe_API_Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Stripe_Restricted_API_Key": r"rk_live_[0-9a-zA-Z]{24}",
    "TryHackMe_CTF_Flag": r"[t|T](?:[r|R][y|Y][h|H][a|A][c|C][k|K][m|M][e|E]|[h|H][m|M])\\{.*\\}$",
    "Twilio_API_Key": r"SK[0-9a-fA-F]{32}",
    "Twitter_Access_Token": r"[t|T][w|W][i|I][t|T][t|T][e|E][r|R].*[1-9][0-9]+-[0-9a-zA-Z]{40}",
    "Twitter_ClientID": r"[t|T][w|W][i|I][t|T][t|T][e|E][r|R](.{0,20})?['\"][0-9a-z]{18,25}",
    "Twitter_OAuth": r"[t|T][w|W][i|I][t|T][t|T][e|E][r|R].*['|\"][0-9a-zA-Z]{35,44}['|\"]",
    "Twitter_Secret_Key": r"[t|T][w|W][i|I][t|T][t|T][e|E][r|R](.{0,20})?['\"][0-9a-z]{35,44}"
}


SensitiveInformation_reg_list = {
    "sfz": r"""['"]((\d{8}(0\d|10|11|12)([0-2]\d|30|31)\d{3}$)|(\d{6}(18|19|20)\d{2}(0[1-9]|10|11|12)([0-2]\d|30|31)\d{3}(\d|X|x)))['"]""",
    
}


black_sniffer_list = [
    "jpg",
    "png",
    "jpeg",
    "gif",
]


balck_domain_list = [
    r'.*w3.org',
    r'.*apache.org',
    r'.*android.com',
    r'.*jpush.cn',
    r'.*umengcloud.com',
    r'.*umeng.com',
    r'.*github.com',
    r'.*w3school.com.cn',
    r'.*apple.com',
    r'.*.amap.com',
    r'.*slf4j.org',
    r'.*baidu.com'
]


web_file_suffix = [
    "html",
    "js",
    "xml",
    "php",
    "jsp",
    "class",
    "asp",
    "aspx",
    "py"
]



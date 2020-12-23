from HTMLParser import HTMLParser
import time
 
class AHREFParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.urls = []
    def handle_starttag(self, tag, attrs):
        if tag == "a": # 開始タグがaであるかどうか判定
            attrs = dict(attrs) # タプルを辞書に変換する
            if 'href' in attrs: # キー値(属性名)がhrefであるか判定
                self.urls.append(attrs['href'])
 
    def handle_endtag(self, tag): # 開始・終了タグに囲まれた中身の処理
        return

def ignoreHexLine(buf):
    lines = buf.split(b"\r\n")
    result = ''
    for line in lines[1::2]:
        result += line
    return result


def getHttp(ssck, hostname, path):
    getRequest = 'GET {0} HTTP/1.1\r\nHost: {1}\r\n\r\n'.format(path, hostname)
    print(getRequest)
    ssck.send(getRequest.encode('utf-8'))
    rawRes = ssck.recv()
    # Header部分を一行ずつパースする
    resList = rawRes.load.split('\r\n')
    BufferBody = ''
    isText = False
    ContentLength = 0
    isChunked = False
    for line in resList:
        print(line)
        # 先頭がContent-Type:の場合
        if line.startswith('Content-Type:'):
            temp = re.search('text/html', line)
            if temp != None:
                isText = True
            else:
                isText = False
        # 先頭がContent-Length:の場合
        if line.startswith('Content-Length:'):
            temp = re.search('[0-9]+', line)
            ContentLength = int(temp.group(0))
        # 先頭がTransfer-Encoding: chunkedの場合
        if line.startswith('Transfer-Encoding:'):
            temp = re.search('chunked', line)
            if temp != None:
                isChunked = True
        # もし空なら次のループ以降がbodyなのでforをbreakする
        if line == '':
            break
    # BufferBodyに最初1パケット分のbodyを追記する
    BufferBody += rawRes.load.split('\r\n\r\n')[1]
    # Bodyのカウンターに最初1パケット分のbodyの追記する
    bodyLen = len(BufferBody)
    if isChunked:
        print("Chunk Mode")
        isEnd = False
        bufferChunk = ''
        while True:
            bufferChunk += ssck.recv().load
            temp = re.search('\n0\r\n\r\n', bufferChunk)
            if temp != None:
                break
        BufferBody += bufferChunk
        BufferBody = ignoreHexLine(BufferBody)
    else:
        # Content Length以上になるまで受信をループする
        while bodyLen != ContentLength:
            chunk = ssck.recv().load
            BufferBody += chunk
            bodyLen += int(len(chunk)) # 受信したサイズをBodyのカウンターにインクリメント
    if path[-1] == '/':
        if path == '/':
            path = 'index.html'
        else:
            path += 'index.html'
    path = './result/' + hostname + "/" + path
    # ファイルを書く
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(path, mode='w') as f:
        f.write(BufferBody)
    return BufferBody

# SteamSocketのOpen
request_hostname = 'ylb.jp'
request_port = 80
request_path = '/'

sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck.connect((request_hostname, request_port))
ssck = StreamSocket(sck)

body = getHttp(ssck, request_hostname, request_path)
parser = AHREFParser()
parser.feed(body)
for link in parser.urls:
    if not link.startswith('http://') and not link.startswith('https://'):
        getHttp(ssck, request_hostname, "/" + link)

parser.close()

# コネクションを閉じる
ssck.close()
sck.close()

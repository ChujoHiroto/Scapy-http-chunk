def ignoreHexLine(buf):
    lines = buf.split(b"\r\n")
    result = ''
    for line in lines[1::2]:
        result += line
    return result


def getHttp(hostname, path):
    # SteamSocketのOpen
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck.connect((hostname, 80))
    ssck = StreamSocket(sck)
    ssck.send('GET {0} HTTP/1.1\r\nHost: {1}\r\n\r\n'.format(path, hostname).encode('utf-8'))
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
        print("end")
    if path == '/':
        path += 'index.html'
    # ファイルを書く
    with open('./result' + path, mode='w') as f:
        f.write(BufferBody)
    # コネクションを閉じる
    ssck.close()
    sck.close()

getHttp('ylb.jp', '/')

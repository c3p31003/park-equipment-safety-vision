from app import app
import ssl

if __name__ == '__main__':
    # SSL 証明書の生成
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        certfile='cert.pem',
        keyfile='key.pem'
    )
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)
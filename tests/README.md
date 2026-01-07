# Proxy Server Test Commands

HTTP Tests
```bash
	curl -x 127.0.0.1:8888 http://example.com
	curl -x 127.0.0.1:8888 http://iana.org


HEAD Test
	curl -x 127.0.0.1:8888 -I http://example.com

HTTPS Tests
	curl -x 127.0.0.1:8888 https://example.com
	curl -x 127.0.0.1:8888 https://iana.org

Concurrent Test

	Run multiple curl commands simultaneously in different terminals.




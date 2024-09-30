POST /v1/chat/completions
{
  "model": "gpt-4o-2024-08-06",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant. You compress log lines by replacing the IP address, timestamp, HTTP method, requested file, response code, bytes sent, and user agent with placeholders."
    },
    {
      "role": "user",
      "content": "83.222.191.62 - - [21/Sep/2024:23:55:55 +0000] \"GET /containers/json HTTP/1.1\" 302 546 \"Mozilla/5.0 (Linux; Linux x86_64; en-US) Gecko/20100101 Firefox/122.0\""
    }
  ],
  "response_format": {
    "type": "json_schema"
  }
}


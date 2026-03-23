# 请求示例 {#request-example}

## Python {#request-example-Python}

```python
# coding=utf-8
import requests


# Get token
# <your_username> 以及 <your_password> 换成您的认证信息
auth_url = 'https://rqdata.ricequant.com/auth'
auth_json = {'user_name': '<your_username>', 'password': '<your_password>'}
token = requests.post(auth_url, json=auth_json).text

# Get data
data_url = 'https://rqdata.ricequant.com/api'
data_json = {'method': 'get_price', 'order_book_ids': ['10001941', '10001943'], 'start_date': '20190601', 'end_date': '20191011'}
headers = {'token': token}
response = requests.post(data_url, json=data_json, headers=headers)

print('resp: ', response.text)

```

## R {#request-example-R}

注：R 中可以通过 reticulate 包直接调用 python 版本的 RQDATAC。

```r
library(httr)

# Get token
# <your_username> 以及 <your_password> 换成您的认证信息
auth_url <- 'https://rqdata.ricequant.com/auth'
auth_json <- list(
        user_name = "your_username",
        password = "your_password"
    )
res <- POST(auth_url, body = auth_json, encode = "json")
tk <- content(res)

# Get data
data_url <- 'https://rqdata.ricequant.com/api'
data_json <- list(
        method = 'get_price',
        order_book_ids = list('000001.XSHE', '00005.XSHE'),
        start_date = '20190601',
        end_date = '20191011'
    )
res <- POST(data_url, body = data_json, add_headers(token=tk), encode="json")

```

## MATLAB {#request-example-MATLAB}

我们提供 MATLAB 客户端产品(toolbox)，提供十分简洁易用的 API，调用方式类似于 python-rqdatac，**请联系我们的销售或者致电公司官方电话获取**。

## PHP {#request-example-PHP}

```PHP
<?php
function doPost($url, $post_data, $token){
    $headers =[
     'token:' . $token,
    ];
    $curl = curl_init();
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_POST, 1);
    $data_string = json_encode($post_data);
    curl_setopt($curl, CURLOPT_POSTFIELDS, $data_string);
    $data = curl_exec($curl);
    curl_close($curl);
    $body = explode("\r\n\r\n", $data, 0);
    return $body;
}

// <your_username> 以及 <your_password> 换成您的认证信息
// Get token
$auth_url = "https://rqdata.ricequant.com/auth";
$auth_json = array(
    "user_name" => "your_username",
    "password" => "your_password",
);
$token = doPost($auth_url, $auth_json,  0);

// Get api data
$api_url = "https://rqdata.ricequant.com/api";
$api_json = array(
    "method" => "get_price",
    "order_book_ids" => array("000001.XSHE", "000005.XSHE"),
    "start_date" => "20190601",
    "end_date" => "20191011"
);

$data = doPost($api_url, $api_json, $token[0]);
print_r($data);
?>

```

## C++ {#request-example-Cjiajia}

使用[cURL](https://github.com/curl/curl)库执行请求

```cpp
#include "iostream"
#include "string"
#include "sstream"
#include "curl/curl.h"
using namespace std;

size_t receive_data(void *ptr, size_t size, size_t nmemb, void *stream){
    string data((const char*) ptr, (size_t) size * nmemb);
    *((stringstream*) stream) << data;
    return size * nmemb;
}

const char *AUTH_URL = "https://rqdata.ricequant.com/auth";
const char *API_URL = "https://rqdata.ricequant.com/api";

string doPost(string json, string token) {
    CURL *newCurl = NULL;
    CURLcode response;
    newCurl = curl_easy_init();
    if ( newCurl != NULL ) {
        stringstream out;
        curl_slist *plist = curl_slist_append(NULL, "Content-Type:application/json");
        if(token != "") {
            plist = curl_slist_append(plist, ("token:" + token).c_str());
            curl_easy_setopt(newCurl, CURLOPT_URL, API_URL);
        } else {
            curl_easy_setopt(newCurl, CURLOPT_URL, AUTH_URL);
        }
        curl_easy_setopt(newCurl, CURLOPT_TIMEOUT, 3);
        curl_easy_setopt(newCurl, CURLOPT_HTTPHEADER, plist);
        curl_easy_setopt(newCurl, CURLOPT_POSTFIELDS, json.c_str());
        curl_easy_setopt(newCurl, CURLOPT_WRITEFUNCTION, receive_data);
        curl_easy_setopt(newCurl, CURLOPT_WRITEDATA, &out);
        curl_easy_setopt(newCurl, CURLOPT_SSL_OPTIONS, CURLSSLOPT_NATIVE_CA);
        response = curl_easy_perform(newCurl);
        curl_easy_cleanup(newCurl);
        newCurl = NULL;
        curl_slist_free_all(plist);
        plist = NULL;
        return out.str();
    }
}

int main() {
    // <your_username> 以及 <your_password> 换成您的认证信息
    // Get token
    const string authJson = "{\"user_name\": \"your_username\",\"password\": \"your_password\"}";
    const string token = doPost(authJson, "");

    // Get api data
    const string dataJson =
        "{"
            "\"method\": \"get_price\", "
            "\"order_book_ids\": [\"000001.XSHE\", \"000005.XSHE\"], "
            "\"start_date\": \"20220702\", "
            "\"end_date\": \"20220722\""
        "}";
    string data = doPost(dataJson, token);
    cout << data << endl;
    return 0;
}

```

<!-- prettier-ignore -->
## C# {#request-example-Cjing}

```cs
using System;
using System.Net;
using System.IO;
using System.Text;

namespace HttpTest
{
    class HttpTest
    {
        public static string DoPost(string url, string content, string token)
        {
            string result = "";
            HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
            req.Method = "POST";
            req.ContentType = "application/json";
            if (token != null){
                req.Headers["token"] = token;
            }

            // Add post parm
            byte[] data = Encoding.UTF8.GetBytes(content);
            req.ContentLength = data.Length;
            using (Stream reqStream = req.GetRequestStream())
            {
                reqStream.Write(data, 0, data.Length);
                reqStream.Close();
            }
            // Get response
            HttpWebResponse resp = (HttpWebResponse)req.GetResponse();
            Stream stream = resp.GetResponseStream();
            using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
            {
                result = reader.ReadToEnd();
            }
            return result;
        }

        public static void Main(string[] args)
        {
            // <your_username> 以及 <your_password> 换成您的认证信息
            // Get token
            string authUrl = "https://rqdata.ricequant.com/auth";
            string authJson = "{\"user_name\": \"your_username\", \"password\": \"your_password\"}";
            string token = DoPost(authUrl, authJson, null);
            Console.WriteLine(token);

            // Get api data
            string apiUrl = "https://rqdata.ricequant.com/api";
            string apiJson = "{" +
                "\"method\": \"get_price\", " +
                "\"order_book_ids\": [\"000001.XSHE\", \"000005.XSHE\"], " +
                "\"start_date\": \"20220702\", " +
                "\"end_date\": \"20220722\"" +
                "}";
            string data = DoPost(apiUrl, apiJson, token);
            Console.WriteLine(data);
        }
    }
}

```

## Java {#request-example-Java}

仅使用内置包。

```java
import javax.net.ssl.HttpsURLConnection;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;

public class HttpTest {

    public static String doPost(URL url, String json, String token) {
        try {
            HttpsURLConnection con = (HttpsURLConnection) url.openConnection();
            con.setDoOutput(true);
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json");
            if (token != null) {
                con.setRequestProperty("token", token);
            }

            OutputStream os = con.getOutputStream();
            byte[] input = json.getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);

            BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream(), StandardCharsets.UTF_8));
            StringBuilder response = new StringBuilder();
            String responseLine;
            while ((responseLine = br.readLine()) != null) {
                response.append(responseLine.trim());
            }
            return response.toString();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public static void main(String[] args) throws Exception {
        // <your_username> 以及 <your_password> 换成您的认证信息
        // Get token
        URL authUrl = new URL("https://rqdata.ricequant.com/auth");
        String authJson = "{\"user_name\": \"your_username\", \"password\": \"your_password\"}";
        String token = doPost(authUrl, authJson, null);

        // Get api data
        URL apiUrl = new URL("https://rqdata.ricequant.com/api");
        String apiJson = "{" +
                "\"method\": \"get_price\", " +
                "\"order_book_ids\": [\"000001.XSHE\", \"000005.XSHE\"], " +
                "\"start_date\": \"20220702\", " +
                "\"end_date\": \"20220722\"" +
                "}";
        String data = doPost(apiUrl, apiJson, token);
        System.out.println(data);
    }
}

```

## Go {#request-example-Go}

```go
package main

import (
    "fmt"
    "io/ioutil"
    "net/http"
    "strings"
)

func doPost(url, data, token string) string {
    request, _ := http.NewRequest("POST", url, strings.NewReader(data))
    if token != "" {
        request.Header.Add("token", token)
    }
    resp, err := http.DefaultClient.Do(request)
    if err != nil {
        fmt.Printf("post data error:%v\n", err)
        return "err"
    }
    respBody, _ := ioutil.ReadAll(resp.Body)
    return string(respBody)
}

func main() {
    // <your_username> 以及 <your_password> 换成您的认证信息
    // Get token
    authUrl := "https://rqdata.ricequant.com/auth"
    authJson := `{"user_name":"your_username","password":"your_password"}`
    token := doPost(authUrl, authJson, "")

    // Get api data
    apiUrl := "https://rqdata.ricequant.com/api"
    dataJson := `{"method": "get_price", "order_book_ids": ["000001.XSHE", "000005.XSHE"], "start_date": "20220702", "end_date": "20220722"}`
    postData := doPost(apiUrl, dataJson, token)
    fmt.Printf("data:%v", postData)
}

```

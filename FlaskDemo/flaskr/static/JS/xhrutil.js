// 创建一个全局xhttp对象，将XMLHttpRequest对象及其方法进行封装
var xhttp = {};

xhttp.quest = function(option, callback){
    var xhr;
    if (window.XMLHttpRequest)
    {
        //  IE7+, Firefox, Chrome, Opera, Safari 浏览器执行代码
        xhr=new XMLHttpRequest();
    }
    else
    {
        // IE6, IE5 浏览器执行代码
        xhr=new ActiveXObject("Microsoft.XMLHTTP");
    }

    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4){
            if(xhr.status >= 200 && xhr.status < 400){
                var result = xhr.responseText;
                var content_type = xhr.getResponseHeader('content-type');
                console.log("responseText is "+result)
                console.log('xhr.status is ',xhr.status)
                console.log(xhr.getAllResponseHeaders());

                if(content_type.includes('application/json')){
                    //如果服务器端返回json字符串，则将json字符串转换为JavaScript对象
                    try {
                        result = JSON.parse(xhr.responseText);
                    } catch(e){
                        alert(e);
                    }
                    if(result.error){
                        callback && callback(result.error,None);
                    }else{
                        callback && callback('',result);
                    }
                }else if(content_type.startsWith('text')){
                    if(result.startsWith('http') || result.startsWith('https')){
                        alert('response is not JSON and content-type is '+content_type);
                        window.location.href = result;
                    }
                }
            }else{
                callback && callback('status:' + xhr.status);
            }
        }
    }
    xhr.open(option.method, option.url, true);
//    console.log(xhr.getResponseHeader('content-type'))
    xhr.setRequestHeader("xhr","True")
    send(xhr,"json",option.data)
};

function send(xhr,type,data) {
    if (type === "formdata") {
        fd = new FormData();
        for(key in data){
            fd.append(key, data[key]);
        }
        data = fd;
    } else if (type === "json") {
        xhr.setRequestHeader("Content-Type", "application/json");
        data = JSON.stringify(data);
    } else if (type === "text") {
        data = data;
    } else if (type === "www") {
        // 这个header 其实是 传统post 表单的格式
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        data = data;
    }
    xhr.send(data);
}

xhttp.get = function(url, callback){
    var option = url.url ? url : { "url": url };
    option.method = 'get';
    this.quest(option, callback);
};

xhttp.post = function(option, callback){
    option.method = 'post';
    this.quest(option, callback);
};

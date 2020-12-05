// 监听页面显示时让搜索框获取焦点，页面切换前正在评论时，页面显示时评论输入框会获取输入焦点
document.addEventListener('visibilitychange',function(){
    if(!document.hidden){
        if(document.getElementById("title_search")){
            document.getElementById("title_search").focus();
        }
    }else{
//        console.log("page is hidden!");
    }
});

function doFavour(method, url, pid){
    var data = {};
    var option = {};

    if(document.getElementById('like'+pid).getAttribute("class").toLowerCase() == "unlike"){
        data = {"pid":pid, "op":"Like"};
    }else{
        data = {"pid":pid, "op":"unLike"};
    }
    option.data = data;
    option.url = url;
    console.log("doFavour to send data: "+JSON.stringify(option));

    if(method.toLowerCase() == 'post'){
        xhttp.post(option, function(error, result){
            if(error == ''){
                if(result.favour == "Like"){
                    document.getElementById('like'+pid).setAttribute("class","like");
                }else if(result.favour == "unLike"){
                    document.getElementById('like'+pid).setAttribute("class","unlike");
                }else if(result.url){
                //                    重定向到登陆页面
                    window.location.href = result.url;
                }else{
                    alert('content-type is '+content_type+' and attr favour in ResponseText is unexpected!');
                    window.history.back(-1);
                }
            }else{
                alert(error + '\nFailed, please try again.');
//                window.history.back(-1);
            }
        });
    }else{
        alert('Not the get or other method and only post method now. ')
    }
}

function toComment(pid){
//    console.log(pid);
//    console.log(document.getElementById(pid));
    var formComment = document.getElementsByClassName('to_comment'+pid)[0];

//    console.log(formComment);
//    console.log(typeof formComment.style['display']);
    if(formComment.style['display'].toLowerCase() == 'none'){
        formComment.style = "display: flex;";
        formComment.getElementsByTagName('textarea')[0].focus();
    }else{
        formComment.style = "display: None;";
    }

}

function doComment(method, url, pid){
    var option = {};
    var data = {};
    var formComment = document.getElementsByClassName('to_comment'+pid)[0];
    data.pid = pid;
    data.comment_body = formComment.getElementsByTagName('textarea')[0].value;
    option.data = data;
    option.url = url;

    console.log("doComment to send data: "+JSON.stringify(option));

    if(method.toLowerCase() == 'post'){
        xhttp.post(option, function(error, result){
            if(error == '' && result.comment){
                var div_comment = document.createElement('div');
                var div_com_about = document.createElement('div');
                var p_com_body = document.createElement('p');

                div_comment.setAttribute('class','comment');
                div_comment.setAttribute('id','comment'+result.comment['id']);
                div_com_about.setAttribute('class','comment_about');
                var comment_about = 'by '+result.comment['username']+' on '+new Date(result.comment['createdTime']).toLocaleString();
                div_com_about.innerHTML = comment_about;
                p_com_body.setAttribute('class','comment_body');
                p_com_body.innerHTML = result.comment['comment'];
                div_comment.appendChild(div_com_about);
                div_comment.appendChild(p_com_body);

                formComment.parentNode.insertBefore(div_comment,formComment);
            }else if(result.error){
                alert(result.error);
            }else{
                alert(error + '\nFailed, please try again.')
            }
        });
    }else{
        alert('Not the get or other method and only post method now. ')
    }

}

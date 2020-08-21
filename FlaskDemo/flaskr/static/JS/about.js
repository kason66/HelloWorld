
for(post in posts ){
    document.getElementById(posts[post]['id']).getElementsByClassName('about')[0].innerHTML=
    "by "+posts[post]['username']+" on " + new Date(posts[post]['created']).toLocaleString();
}




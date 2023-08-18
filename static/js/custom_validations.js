function navbar_active(){
    $(document).ready(function(){
        $(".active").removeClass("active");
        $("this").addClass("active");
 });
}

// function validate(event) {
//     v = document.getElementById("email").value;
//     if (v.indexOf("@") == -1) {
//         event.preventDefault();
//         alert("Enter a valid email")
//         return false;
//     }
//     return true;
// }

async function like(blogId) {
    const likeCount = document.getElementById('like-count-' + blogId);
    let icon = document.querySelector('.like-icon-'+ blogId);
    console.log(icon)
    console.log(icon.classList)

    fetch('/like_post/' + blogId, { method: "POST" })
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            likeCount.innerHTML = data["likes"] + " likes";
            if (data["liked"] == true) {
                console.log("True")
                icon.classList.remove("far");
                icon.classList.add("fas");

            } else {
                console.log("False")
                icon.classList.remove("fas");
                icon.classList.add("far");

            }
        })

}

function send_like(event){
    article = event.target;
    member_id = article.dataset.member_id;
    console.log(member_id);
    like(member_id);
}

function initialize(){
    like_buttons = document.querySelectorAll(".fa-heart");
    for (const like_button of like_buttons) {        
        like_button.onclick = send_like;
    }
}

$(document).ready(function(){
    $('.comment').on('click',function(e){
        console.log("Clicked")
        e.preventDefault();
        var member_id = $(this).attr('member_id');
        // var comment = document.getElementById(member_id).value;
        var comment = $('#'+'blog-'+member_id).val();
        console.log(member_id)
        console.log(comment)

        if (comment.length!=0){
            req = $.ajax({
                url : '/add_comment/'+ member_id,
                type: 'POST',
                data:  {comment:comment}
            });
            req.done(function(data){
                console.log(comment);
                document.getElementById('blog-'+member_id).value='';

                var comment_count = document.querySelectorAll("#comment-count-"+member_id);
                console.log(comment_count);
                
                var ul = document.getElementById("comment-"+member_id);
                var li = document.createElement('li');
                var div1 = document.createElement('div');
                var div2 = document.createElement('div');
                var div3 = document.createElement('div');
                var a1 = document.createElement('a');
                var img = document.createElement('img');
                var a2 = document.createElement('a');
                
                var p = document.createElement('p');
                var i = document.createElement('i');
                var i2 = document.createElement('i');

                li.setAttribute('id','comment-delete-'+data.c_id);
                div1.setAttribute('class','c');
                div2.setAttribute('class','title')
                div3.setAttribute('class','info');
                a1.setAttribute('class','image')
                a2.setAttribute('href',"/profile/"+data.username);

                i.setAttribute('id',data.c_id);
                i.setAttribute('href','/delete_comment/'+data.c_id);
                i.setAttribute('class','delete_comment fa-sharp fa-solid fa-trash float-sm-right');

                i2.setAttribute('class','fa fa-comments');  
                i2.setAttribute('aria-hidden','true');             

                img.setAttribute('src',data.image);
                img.setAttribute('width',44);
                img.setAttribute('height',44);                
                
                p.innerHTML = data.comment;

                div3.innerHTML = '1 second ago';

                a2.innerHTML = data.fname+" "+data.lname;
                for (let i=0; i<comment_count.length;i++){
                    comment_count[i].innerHTML = " " + data.comment_count + " comments";
                }

                li.appendChild(a1).appendChild(img);            
                li.appendChild(div1).appendChild(div2).appendChild(a2);                    
                li.appendChild(div1).appendChild(div2)
                li.appendChild(div1).appendChild(div3);
                li.appendChild(div1).appendChild(p);
                li.appendChild(div1).appendChild(p).appendChild(i);
                ul.insertBefore(li, ul.lastElementChild);

                // document.getElementById("#comment-form-"+member_id).reset();

                $('.delete_comment').on('click',function(ev){
                    ev.preventDefault();
                    var commentId = $(this).attr('id');
                    var div = document.getElementById('comment-delete-'+commentId);
                    var comment_count = document.querySelectorAll("#comment-count-"+member_id);
                    console.log(commentId)
                    console.log(comment_count)
            
                    fetch('/delete_comment/' + commentId, { method: "POST" })
                        .then((res) => res.json())
                        .then((data) => {
                            console.log(data);
                            div.remove();
                            for (let i=0; i<comment_count.length;i++){
                                comment_count[i].innerHTML = " " + data.comment_count + " comments";
                            }           
                            
                    })
                });
                
            });
        }
        return false;
    });

    
});


$(document).ready(function(){
    $('.delete_comment').on('click',function(ev){
        ev.preventDefault();
        var commentId = $(this).attr('id');
        var member_id = $(this).attr('blog_id');
        var div = document.getElementById('comment-delete-'+commentId);
        var comment_count = document.querySelectorAll("#comment-count-"+member_id);
        console.log(commentId)

        fetch('/delete_comment/' + commentId, { method: "POST" })
            .then((res) => res.json())
            .then((data) => {
                console.log(data);
                div.remove();
                for (let i=0; i<comment_count.length;i++){
                    comment_count[i].innerHTML = " " + data.comment_count + " comments";
                }                  
                
        })
    });
});

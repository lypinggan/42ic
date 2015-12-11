/**
Js前台模板
*/
var user_init_login ="";




/**
 * 开启对话框
 */
function dialog(title,value){
     var html = "<div class='dialog'><div class='dialog-inner'><div class='dialog-hd dialog-hd-closable'><span class='dialog-title'>"+title+"</span><a href='#' class='dialog-close' onclick='dialog-closen();'>×</a></div><div class='dialog-bd'>"+value+"</div></div></div>";
     $("body").append( html );
}

var user_id = 0;
var user_username = '';
var user_icon = '';
var user_role = 0;
var t=Math.random();
$(function(){
/**
*初始化默认值插件
*/
jQuery('.input').defaultValue();

/**
* 输入框自动伸缩
*/
        $('textarea').elastic();
        $('textarea').trigger('update');

/**
* 回到顶部
*/
        $("#go-to-top").click(function(){
                $("html, body").animate({'scrollTop': 0}, 400);
                return false;
        });
        $(window).scroll(function() {
                var top = $(document).scrollTop();
                var g = $("#go-to-top");
                if (top > 300 && g.is(":hidden")) {
                        g.fadeIn();
                } else if(top < 300 && g.is(":visible")) {
                        g.fadeOut();
                }
        }); 
        

/**列表fdbar触发，显示时间、作者等信息*/
$(".sdw").mouseover(function(){
         $(this).find(".fdbar").show();
});
$(".sdw").mouseout(function(){
         $(this).find(".fdbar").hide();
});
/**
$.get("/ajax/messages/"+t, function(data){
  $("#messages").html( data );
}); 
*/
/**
* 左右键翻页
*/
$(window).keydown(function(event){
  if(event.keyCode == '37') {
          var sprev_url = $(".sprev").attr("href");
          if(sprev_url){
          location.href=sprev_url; 
      }
  }
  if(event.keyCode == '39') {
          var snext_url = $(".snext").attr("href");
          if(snext_url){
          location.href=snext_url; 
      }
  }
}); 
/**
 * 输入框获得焦点
 * 修改边框颜色
 * */
$(":input").focus(function(){
                          $(this).addClass("focus");
                }).blur(function(){
                          $(this).removeClass("focus");
});

/**
 * 顶部搜素框
 * */
$("#search-query").focus(function(){
                        //获得焦点，显示提示
                          $(".search-result").css("display","block");
                }).blur(function(){
                        //失去焦点，隐藏提示
                          $(".search-result").css("display","none");
});
/***
//关键词发送改变时触发
$("#search-query").focus(function(){
    $(this).bind("keyup", function(){
    var keywords = $(this).val();
    if(keywords == ''){
        $(".search-result").html("请输入关键字");
    }else{
        $.get("/search/ajax_question?q="+keywords, function(data){
                $(".search-result").html(data);
        });
        }
    });
    
    
    //alert(keywords);
        

    
});
**/


})

$(function(){
var q_id = $("input[name='question_id']").val();
var t=Math.random();
var uid = 0;
var answer_permissions = 0;
var num_follow = 0;
var num_votes = 0;
var is_follow = 0;
var is_votes = 0;
$.getJSON("/ajax/question_view/"+q_id+"/"+t, function(json){
  uid = json.uid;
  answer_permissions = json.answer_permissions;
  num_follow = json.num_follow;
  num_votes = json.num_votes;
  is_follow = json.is_follow;
  is_votes = json.is_votes;
  //更新关注、喜欢的人数
  update_follow_num( num_follow );
  update_votes_num( num_votes );
  //更新关注、喜欢的状态
  update_votes_mode( is_votes );
  update_follow_mode( is_follow );
});

//点击喜欢按钮
$(".btn-votes").bind("click",function(){
		var t=Math.random();
		if ( uid==0 ){
			jAlert("对不起，您没有权限操作或还没登录",'错误');
			}else{
				if( is_votes ){
			        $.getJSON("/ajax/question_downvote/"+q_id+"/"+t, function(json){
						if(json.ok){
							num_votes = json.num_votes;
							update_votes_num( num_votes );
							is_votes = 0;
							update_votes_mode( is_votes );
							}
			       });
				}else{
					$.getJSON("/ajax/question_upvote/"+q_id+"/"+t, function(json){
						if(json.ok){
							num_votes = json.num_votes;
							update_votes_num( num_votes );
							is_votes = 1;
							update_votes_mode( is_votes );
							}
			       });
				}
			}
		return false;
});
//点击关注按钮
$(".btn-follow").bind("click",function(){
		var t=Math.random();
		if ( uid==0 ){
			jAlert("对不起，您没有权限操作或还没登录",'错误');
			}else{
				if( is_follow ){
			        $.getJSON("/ajax/question_downfollow/"+q_id+"/"+t, function(json){
						if(json.ok){
							num_follow = json.num_follow;
							update_follow_num( num_follow );
							is_follow = 0;
							update_follow_mode( is_follow );
							}
			       });
				}else{
					$.getJSON("/ajax/question_upfollow/"+q_id+"/"+t, function(json){
						if(json.ok){
							num_follow = json.num_follow;
							update_follow_num( num_follow );
							is_follow = 1;
							update_follow_mode( is_follow );
							}
			       });
				}
			}
		return false;
});
//点击回复图标
$(".reply_at").bind("click",function(){
		var name = $(this).prev().html();
		$("#wmd-input").append('@'+name+" ");
		$("#wmd-input").focus();
});
//点击设为正确答案
$(".a_mtra").bind("click",function(){
		var answer_id = $(this).attr("data-aid");
		url = "/question/make_the_right_answer/"+answer_id;
		jConfirm("此操作不能取消，请确认是否就是您想要的答案，否则请取消",'请确认', function(r) {
			if(r){
			    location_href(url);
			}
		});
});
//点击感谢他
$(".a_thinkhim").bind("click",function(){
		var answer_id = $(this).attr("data-aid");
		url = "/question/thankhim/"+answer_id;
		$.getJSON(url, function(json){
			if(json.status){
			jAlert(json.value,'成功');
			}else{
			jAlert(json.value,'失败');
			}
		});

});
//点击评论
$(".a_get_answer_comment").bind("click",function(){
		var answer_id = $(this).attr("data-aid");
		url = "/ajax/get_answer_comment/"+answer_id+"/"+t;
		$.get(url, function(data){
		  if(data=='no'){
		    var formhtml = '<div class="recreplylst"></div>';
		    formhtml += '<form method="post" rev="/ajax/saying_comment" class="reply a_saying_comment_form" name="" action="/ajax/saying_comment"><span class="pl"></span><input type="text" name="comment" style="width:330px;margin-left:28px"><input type="submit" value="发表回应"><input name="aid" type="hidden" value="'+answer_id+'"></form>';
		    $('#sd-'+answer_id).append(formhtml);
		}else{
			$('#sd-'+answer_id).append(data);
			}
		});

});
//点击评论
$(".a_saying_comment_form").bind("click",function(){
		var answer_id = $(this).attr("data-aid");
		url = "/ajax/saying_comment/"+answer_id+"/"+t;
		$.get(url, function(data){
		  if(data=='no'){
		    var formhtml = '<form method="post" rev="/ajax/saying_comment" class="reply a_saying_comment_form" name="" action="/ajax/saying_comment"><span class="pl"></span><input type="text" name="comment" style="width:330px;margin-left:28px"><input type="submit" value="发表回应"><input name="aid" type="hidden" value="'+answer_id+'"></form>';
		    $('#sd-'+answer_id).append(formhtml);
		}else{
			$('#sd-'+answer_id).append(data);
			}
		});

});

//激活输入答案
//如果没有权限，则报错
$("#wmd-input").bind("focus",function(){
		if ( answer_permissions==0 ){
			jAlert("对不起，您没有权限操作或还没登录",'错误');
			$(this).html('');
			}
		return false;
});
//页面跳转
location_href = function( url ) {
	location.href = url;
}

//更新喜欢状态
update_votes_mode = function( is_votes ) {
    if ( is_votes > 0 ){
	      $(".btn-votes").removeClass("votes-add").addClass("votes-cancel").attr('title', '取消喜欢?');
	  }else{
		  $(".btn-votes").addClass("votes-add").removeClass("votes-cancel").attr('title', '标为喜欢?');
	  }
}
//更新关注状态
update_follow_mode = function( is_follow ) {
    if ( is_follow ){
	      $(".btn-follow").removeClass("follow-add").addClass("follow-cancel").attr('title', '取消关注?');
	  }else{
		  $(".btn-follow").addClass("follow-add").removeClass("follow-cancel").attr('title', '标为关注?');
	  }
}
//更新喜欢人数
update_votes_num = function( num_votes ) {
	if ( num_votes > 0){
      $(".votes-num").html(num_votes+"人");
    }else{
	  $(".votes-num").html("");
	}
}
//更新关注人数
update_follow_num = function( num_follow ) {
	if (num_follow > 0 ){
      $(".follows-num").html(num_follow+"人");
    }else{
	  $(".follows-num").html("");
	}
}









})
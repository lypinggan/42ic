(function(){var a=window.dui||{},c="dui-dialog",f=[],e=null,d=($.browser.msie&&$.browser.version==="6.0")?true:false,g={},b={};_CSS_DLG="dui-dialog",_CSS_BTN_CLOSE="dui-dialog-close",_CSS_DIV_SHD="dui-dialog-shd",_CSS_DIV_CONTENT="dui-dialog-content",_CSS_IFRM="dui-dialog-iframe",_TXT_CONFIRM="确定",_TXT_CANCEL="取消",_TXT_TIP="提示",_TXT_LOADING="下载中，请稍候...",_templ='<div id="{ID}" class="'+_CSS_DLG+'" style="{CSS_ISHIDE}">				<span class="'+_CSS_DIV_SHD+'"></span>				<div class="'+_CSS_DIV_CONTENT+'">					{TITLE}					<div class="bd"></div>                    {BN_CLOSE}				</div>			</div>',_templ_btn_close='<a href="#" class="'+_CSS_BTN_CLOSE+'">X</a>',_templ_title='<div class="hd"><h3>{TITLE}</h3></div>',_templ_iframe='<iframe class="'+_CSS_IFRM+'"></iframe>',_button_config={confirm:{text:_TXT_CONFIRM,method:function(h){h.close()}},cancel:{text:_TXT_CANCEL,method:function(h){h.close()}}},_default_config={url:"",content:"",title:_TXT_TIP,width:0,height:0,visible:false,iframe:false,maxWidth:960,autoupdate:false,cache:true,buttons:[],callback:null,dataType:"text",isStick:false,isHideClose:false,isHideTitle:false},_config=function(l,k){var h={},j;for(j in k){if(k.hasOwnProperty(j)){h[j]=l[j]||k[j]}}return h},_formCollection=function(n){var k=n.elements,j=0,l,m=[],h={"select-one":function(i){return encodeURIComponent(i.name)+"="+encodeURIComponent(i.options[i.selectedIndex].value)},"select-multiple":function(r){var q=0,p,o=[];for(;p=r.options[q++];){if(p.selected){o.push(encodeURIComponent(r.name)+"="+encodeURIComponent(p.value))}}return o.join("&")},radio:function(i){if(i.checked){return encodeURIComponent(i.name)+"="+encodeURIComponent(i.value)}},checkbox:function(i){if(i.checked){return encodeURIComponent(i.name)+"="+encodeURIComponent(i.value)}}};for(;l=k[j++];){if(h[l.type]){m.push(h[l.type](l))}else{m.push(encodeURIComponent(l.name)+"="+encodeURIComponent(l.value))}}return m.join("&").replace(/\&{2,}/g,"&")},dialog=function(h){var i=h||{};this.config=_config(i,_default_config);this.init()};dialog.prototype={init:function(){if(!this.config){return}this.render();this.bind()},render:function(){var h=this.config,i=c+f.length;f.push(i);$("body").append(_templ.replace("{ID}",i).replace("{CSS_ISHIDE}",h.visible?"":"visibility:hidden;top:-999em;left:-999em;").replace("{TITLE}",_templ_title.replace("{TITLE}",h.title)).replace("{BN_CLOSE}",_templ_btn_close));this.id=i;this.node=$("#"+i);this.title=$(".hd",this.node);this.body=$(".bd",this.node);this.btnClose=$("."+_CSS_BTN_CLOSE,this.node);this.shadow=$("."+_CSS_DIV_SHD,this.node);this.iframe=$("."+_CSS_IFRM,this.node);this.set(h)},bind:function(){var h=this;$(window).bind({resize:function(){if(d){return}h.updatePosition()},scroll:function(){if(!d){return}h.updatePosition()}});this.btnClose.click(function(i){h.close();i.preventDefault()});$("body").keypress(function(i){if(i.keyCode===27){h.close()}})},updateSize:function(){var j=this.node.width(),k,l=$(window).height(),i=this.config;$(".bd",this.node).css({height:"auto","overflow-x":"visible","overflow-y":"visible"});k=this.node.height();if(j>i.maxWidth){j=i.maxWidth;this.node.css("width",j+"px")}if(k>l){$(".bd",this.node).css({height:(l-150)+"px","overflow-x":"hidden","overflow-y":"auto"})}k=this.node.height();this.shadow.width(j+16).height(k+16);this.iframe.width(j+16).height(k+16)},updatePosition:function(){if(this.config.isStick){return}var i=this.node.width(),k=this.node.height(),l=$(window),j=d?l.scrollTop():0;this.node.css({left:Math.floor(l.width()/2-i/2-8)+"px",top:Math.floor(l.height()/2-k/2-8)+j+"px"})},set:function(m){var o,q,i,j,h=this.id,k=[],l=this,p=function(r){k.push(0);return h+"-"+r+"-"+k.length};if(!m){return}if(m.width){this.node.css("width",m.width+"px");this.config.width=m.width}if(m.height){this.node.css("height",m.height+"px");this.config.height=m.height}if($.isArray(m.buttons)&&m.buttons[0]){j=$(".ft",this.node);i=[];$(m.buttons).each(function(){var s=arguments[1],r=p("bn");if(typeof s==="string"&&_button_config[s]){i.push('<span class="bn-flat"><input type="button" id="'+r+'" class="'+c+"-bn-"+s+'" value="'+_button_config[s].text+'" /></span> ');b[r]=_button_config[s].method}else{i.push('<span class="bn-flat"><input type="button" id="'+r+'" class="'+c+'-bn" value="'+s.text+'" /></span> ');b[r]=s.method}});if(!j[0]){j=this.body.parent().append('<div class="ft">'+i.join("")+"</div>")}else{j.html(i.join(""))}$(".ft input",this.node).click(function(s){var r=b[this.id];if(r){r(l)}});this.footer=$(".ft",this.node)}else{this.footer=$(".ft",this.node);this.footer.html("")}if(typeof m.isHideClose!=="undefined"){if(m.isHideClose){this.btnClose.hide()}else{this.btnClose.show()}this.config.isHideClose=m.isHideClose}if(typeof m.isHideTitle!=="undefined"){if(m.isHideTitle){this.title.hide()}else{this.title.show()}this.config.isHideTitle=m.isHideTitle}if(m.title){this.setTitle(m.title);this.config.title=m.title}if(typeof m.iframe!=="undefined"){if(!m.iframe){this.iframe.hide()}else{if(!this.iframe[0]){this.node.prepend(_templ_iframe);this.iframe=$("."+_CSS_IFRM,this.node)}else{this.iframe.show()}}this.config.iframe=m.iframe}if(m.content){this.body.html(typeof m.content==="object"?$(m.content).html():m.content);this.config.content=m.content}if(m.url){if(m.cache&&g[m.url]){if(m.dataType==="text"||!m.dataType){this.setContent(g[m.url])}if(m.callback){m.callback(g[m.url],this)}}else{if(m.dataType==="json"){this.setContent(_TXT_LOADING);if(this.footer){this.footer.hide()}$.getJSON(m.url,function(r){l.footer.show();g[m.url]=r;if(m.callback){m.callback(r,l)}})}else{this.setContent(_TXT_LOADING);if(this.footer){this.footer.hide()}$.ajax({url:m.url,dataType:m.dataType,success:function(r){g[m.url]=r;if(l.footer){l.footer.show()}l.setContent(r);if(m.callback){m.callback(r,l)}}})}}}var n=m.position;if(n){this.node.css({left:n[0]+"px",top:n[1]+"px"})}if(typeof m.autoupdate==="boolean"){this.config.autoupdate=m.autoupdate}if(typeof m.isStick==="boolean"){if(m.isStick){this.node[0].style.position="absolute"}else{this.node[0].style.position=""}this.config.isStick=m.isStick}return this.update()},update:function(){this.updateSize();this.updatePosition();return this},setContent:function(h){this.body.html(h);return this.update()},setTitle:function(h){$("h3",this.title).html(h);return this},submit:function(j){var h=this,i=$("form",this.node);i.submit(function(n){n.preventDefault();var k=this.getAttribute("action",2),l=this.getAttribute("method")||"get",m=_formCollection(this);$[l.toLowerCase()](k,m,function(o){if(j){j(o)}},"json")});i.submit()},open:function(){this.node.appendTo("body").css("visibility","visible").show();var h=this,i=h.body[0];h.contentHeight=i.offsetHeight;this.watcher=!this.config.autoupdate?0:setInterval(function(){if(i.offsetHeight===h.contentHeight){return}h.update();h.contentHeight=i.offsetHeight},100);return this},close:function(){this.node.hide();clearInterval(this.watcher);return this}};a.Dialog=function(h,i){if(!i&&e){return h?e.set(h):e}if(!e&&!i){e=new dialog(h);return e}return new dialog(h)};window.dui=a})();
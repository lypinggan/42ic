#coding:utf-8
import math
from cStringIO import StringIO
import Image,ImageFile,ImageEnhance,ImageDraw,ImageFont
import os,uuid

def picopen(image):
    if not image:return

    if hasattr(image, 'getim'): # a PIL Image object
        im = image
    else:
        if not hasattr(image, 'read'): # image content string
            image = StringIO(image)
        try:
            im = Image.open(image) # file-like object
        except IOError, e:
            return

    if im.mode == 'RGBA':
        p = Image.new('RGBA', im.size, 'white')
        try:
            x, y = im.size
            p.paste(im, (0, 0, x, y), im)
            im = p
        except:
            pass
        del p

    if im.mode == 'P':
        need_rgb = True
    elif im.mode == 'L':
        need_rgb = True
    elif im.mode == 'CMYK':
        need_rgb = True
    else:
        need_rgb = False

    if need_rgb:
        im = im.convert('RGB', dither=Image.NONE)

    return im


def pic_resize_width_cut_height_if_large(image, width, max_height=None):
    if not image:return
    if max_height == None:
        max_height = width*2.5

    x, y = image.size
    if x != width:
        image = image.resize((width, (width*y)/x), Image.ANTIALIAS)

    if max_height:
        x, y = image.size
        if y > max_height:
            image = image.crop((0, 0, x, max_height))
    return image


def pic_fit_width_cut_height_if_large(image, width, max_height=None):
    if not image:return

    x, y = image.size
    if x > width:
        image = image.resize((width, (width*y)/x), Image.ANTIALIAS)

    if max_height:
        x, y = image.size
        if y > max_height:
            image = image.crop((0, 0, x, max_height))
    return image


def pic_zoom_outer(image, width, height, max_width, max_height):
    x, y = image.size
    if x < width:
        image = image.resize((width, (width*y)/x), Image.ANTIALIAS)

    if y > max_height:
        image = image.crop((0, 0, x, max_height))
    elif y < height:
        image = image.resize(((height*x)/y, height), Image.ANTIALIAS)

    x, y = image.size

    if x > max_width:
        image = image.crop((0, 0, max_width, y))

    return image


def pic_zoom_inner(image, width, height=None):
    if height == None:
        height = width

    x, y = image.size
    if x > width or y > height:
        #x*height > width*y 缩放到height,剪裁掉width
        x_h = x*height
        w_y = width*y

        if x_h <= w_y:
            cuted_height = height
            cuted_width = x*height//y
        else:
            cuted_height = y*width//x
            cuted_width = width
        image = image.resize((cuted_width, cuted_height), Image.ANTIALIAS)

    return image


def pic_fit(image, width, height=None):
    if height == None:
        height = width

    x, y = image.size
    if x != width or y != height:
        #x*height > width*y 缩放到height,剪裁掉width
        x_h = x*height
        w_y = width*y

        if x_h != w_y:
            if x_h > w_y:
                cuted_height = height
                cuted_width = x*height//y
            else:
                cuted_height = y*width//x
                cuted_width = width
        else:
            cuted_width = width
            cuted_height = height
        image = image.resize((cuted_width, cuted_height), Image.ANTIALIAS)

        x, y = image.size

        if x_h != w_y:
            if x_h > w_y:
                width_begin = (x-width)//4
                height_begin = 0
            else:
                width_begin = 0
                height_begin = (y-height)//4

            image = image.crop((width_begin, height_begin, width_begin+width, height_begin+height))
    return image


def pic_fit_height_if_high(image, width, height=None):
    if height == None:
        height = width

    x, y = image.size
    if x < y:
        p = Image.new('RGBA', (y, y), 'white')
        p.paste(image, ((y-x)//2, 0))
        image = p
        del p
    return pic_fit(image, width, height)


def _calc_square(x, y, width, top_left, size, zoom_out):
    height_delta = width
    default = True # 是否使用默认缩放策略
    if top_left is not None:
        try:
            ax, ay = top_left
            if ax < 0 or ay < 0:
                default = True
            elif size <= 0:
                default = True
            elif ax + size > x:
                default = True
            elif ay + size > y:
                default = True
            else:
                # 用户指定了合法的参数，则使用用户指定缩放策略
                default = False
        except:
            pass

    resize = None
    if default:
        zoom_in = (x > width and y > width)
        background = (x < width or y < width)

        # 如果图过小，需要粘贴在一个白色背景的图片上
        px, py = (width-x)/2, (width-y)/2
        if px < 0:
            px = 0
        if py < 0:
            py = 0
        paste = (px, py)

        # 如果允许放大，就不再需要往白色背景图片上粘贴
        if zoom_out and background:
            zoom_out = x < y and 'x' or 'y'
            if zoom_out == 'x':
                nx = width
                ny = width*y/x
            else:
                nx = width*x/y
                ny = width
            resize = (nx, ny)

            x, y = resize
            ax, ay = (x-width)/2, (y-width)/2
            if ax < 0:
                ax = 0
            if ay < 0:
                ay = 0
            bx = ax + width
            by = ay + width
        else:
            # 计算如何缩小
            if x > width and y > width:
                if x > y:
                    ax, bx = (x-y)/2, (x+y)/2
                    ay, by = 0, y
                else:
                    ax, bx = 0, x
                    ay, by = (y-x)/2, (y+x)/2
                    height_delta = x
            else:
                ax, ay, bx, by = (x-width)/2, (y-width)/2, (x+width)/2, (y+width)/2
                if ax < 0:
                    bx += ax
                    ax = 0
                if ay < 0:
                    by += ay
                    ay = 0

        # 高 > 宽时，需要调整，上方、下方切掉的区域高度比例要是 1:3。
        if y > x and y > width:
            ay -= (y - height_delta) / 4
            by -= (y - height_delta) / 4
        if bx > x:
            bx = x
        if by > y:
            by = y
        crop = [ax, ay, bx, by]
    else:
        zoom_in = (size != width)
        crop = [ax, ay, ax + size, ay + size]
        background = False
        paste = (0, 0)
    return zoom_out, resize, crop, zoom_in, background, paste


def pic_square(im, width, top_left=None, size=0, zoom_out=True):

    x, y = im.size
    zoom_out, resize, crop, zoom_in, background, paste =      \
            _calc_square(x, y, width, top_left, size, zoom_out)

    if zoom_out and resize:
        im = im.resize(resize, Image.ANTIALIAS)

    (ax, ay, bx, by) = crop
    if not ((ax, ay) == (0, 0) and (bx, by) == im.size):
        im = im.crop(crop)

    if not (zoom_out and resize):
        if zoom_in:
            try:
                im = im.resize((width, width), Image.ANTIALIAS)
            except:
                raise PictureError
        if background:
            p = Image.new('RGBA', (width, width), 'white')
            p.paste(im, paste)
            im = p
            del p

    return im


def pic_merge(im1, im2):
    x1, y1 = im1.size
    x2, y2 = im2.size
    bg = Image.new('RGB', ((max(x1, x2), y1+y2+10)), (255, 255, 255))
    bg.paste(im1, (0, 0, x1, y1))
    bg.paste(im2, (0, y1+10, x2, 10+y1+y2))
    return bg


def WaterMark(fil, dh='y'):
    '''
    第一个参数是 图片的完整路径
    第二个参数表示是否对logo图像进行透明处理
    PIL简单 就PIL OpenCV虽然速度快 写起来也多要好多行啊
    '''
    img1 = Image.open(fil).convert("RGB")
    logoimg = Image.open(logo).convert("RGBA")
    
    #这里是针对
    w2 = (img1.size[0] - 10)/5
    h2 = w2*logoimg.size[1]/logoimg.size[0]
    logoimg = logoimg.resize((w2, h2), Image.ANTIALIAS)
    
    #在属主图像中生成嵌入图像大小的box
    box = (img1.size[0] - w2 - 20, img1.size[1] - h2 - 20)
    if 'y' in dh:
        Mask = logoimg.convert("L").point(lambda x: min(x, 100))
        logoimg.putalpha(Mask)
    img1.paste(logoimg, box, logoimg)
    img1.save(fil.split(".")[0]+"_W.jpg")

#--------------------------------------------------------------
def WriteText(img, text = None, savename = None):
    '''
    align 表示对齐方式 1 为右下脚 0 为底部居中
    text 表示要写到图片上的文字
    如果需要在linux下用把请修改字体路径和字体, 
    然后确保安装了python和pil模块
    
    这里没有用OpenCV是因为 官方库 暂时不支持中文
    如果要用中文  就要C++ 用国内爱好这开发的 第三方扩展了 
    所以 直接PIL了
    '''
    if not text:
        text = 'www.42ic.com'   
    
    #img = Image.open(im).convert("RGB")
    Draw = ImageDraw.ImageDraw(img, "RGBA")
    
    #自动调整字体大小
    size = 0
    while True:
        size += 1
        #如果在linux下 请去/usr/share/fonts下找个truetype吧　支持中文的字体
        font = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", size)
        tw, th = font.getsize(text)
        #水印宽度大于图片宽度的1/5
        if tw > img.size[0]/5:
            break

    w1 = img.size[0]*0.78
    #如果是大图片，水印高度在图片顶部往下50，小图片为15
    if img.size[1] > 300:
        h1 = 50
    else:
        h1 = 15
    
    Draw.setfont(font)
    Draw.text((w1, h1), unicode(text, "utf-8"))
    img.save(savename)

class Graphics:    
    def __init__(self,uploadedfile,targetpath,imagename):
        '''初始化参数'''
        self.uploadedfile=uploadedfile
        self.targetpath = targetpath
        self.imagename = imagename

    def check_folder(self, targetpath):
        '''检查目标文件夹是否存在，不存在则创建之'''
        if not os.path.isdir(targetpath):
            os.mkdir(targetpath)
        return targetpath

    def pic_info(self, img):
        '''获取照片的尺寸和确定图片横竖版'''
        w, h = img.size
        if  w>h:
            return w, h, 0  #横版照片
        else:
            return w, h, 1  #竖版照片

    def comp_ratio(self, x, y):
        '''计算比例.'''
        x = float(x)
        y = float(y)
        return float(x/y)

    def pic_cut(self, image, p_w, p_h):
        '''根据设定的尺寸，对指定照片进行像素调整
        图形不会变形 如果指定尺寸比例和原图比例不
        相等时，最大范围剪切'''
        #获取指定照片的规格，一般是1024,768       
        img = image   
        w, h, isVertical = self.pic_info(img)
        #判断照片横竖，为竖版的话对调w,h
        if isVertical:
            p_w, p_h = p_h, p_w

        #如果照片调整比例合适，直接输出
        if self.comp_ratio(p_h, p_w) == self.comp_ratio(h, w):
            target = img.resize((int(p_w), int(p_h)),Image.ANTIALIAS)#hack:高保真必备！                            
            # ANTIALIAS: a high-quality downsampling filter
            # BILINEAR: linear interpolation in a 2x2 environment
            # BICUBIC: cubic spline interpolation in a 4x4 environment
            return target

        #比例不合适就需要对照片进行计算，保证输出照片的正中位置
        #算法灵感来源于ColorStrom
        if self.comp_ratio(p_h, p_w) > self.comp_ratio(h, w):
            #偏高照片的处理
            #以高为基准先调整照片大小
            #根据新高按比例设置新宽
            p_w_n = p_h * self.comp_ratio(w,h) 
            temp_img = img.resize((int(p_w_n), int(p_h)),Image.ANTIALIAS)

            #获取中间选定大小区域
            c = (p_w_n - p_w)/2 #边条大小
            box = (c, 0, c+p_w, p_h) #选定容器
            #换成crop需要的int形参数
            box = tuple(map(int, box)) 
            target = temp_img.crop(box)

            return target

        else:
            #偏宽的照片
            #以宽为基准先调整照片大小
            p_h_n = p_w * self.comp_ratio(h, w)  # 根据新宽按比例设置新高
            temp_img = img.resize((int(p_w), int(p_h_n)),Image.ANTIALIAS)

            #获取新图像
            c = (p_h_n - p_h)/2
            box = (0, c, p_w, c+p_h)
            box = tuple(map(int, box))
            target = temp_img.crop(box)

            return target
        
    def pic_zoom_w(self, image, p_w):
        '''根据设定的宽度，对指定照片进行像素缩放 图形不会变形
        图形比例不变 高度根据指定的宽度等比列放大缩小'''
        #获取指定照片的规格，一般是1024,768       
        img = image   
        w, h, isVertical = self.pic_info(img)
        p_h=p_w * self.comp_ratio(h, w)
        temp_img = img.resize((int(p_w), int(p_h)),Image.ANTIALIAS)
        
        box = (0, 0, p_w, p_h)
        box = tuple(map(int, box))
        target = temp_img.crop(box)

        return target
    
    def pic_zoom_h(self, image, p_h):
        '''根据设定的高度，对指定照片进行像素缩放 图形不会变形
        图形比例不变 宽度根据指定的高度等比列放大缩小'''
        #获取指定照片的规格，一般是1024,768       
        img = image   
        w, h, isVertical = self.pic_info(img)
        p_w=p_h * self.comp_ratio(w, h)
        temp_img = img.resize((int(p_w), int(p_h)),Image.ANTIALIAS)
        
        box = (0, 0, p_w, p_h)
        box = tuple(map(int, box))
        target = temp_img.crop(box)

        return target   

    #外部调用方法
    def run_cut(self,quality=80,*args):
        '''运行调整照片尺寸进程 接纳规格列表，每个规格为一个tuple'''
        parser = ImageFile.Parser()  
        for chunk in self.uploadedfile.chunks():  
            parser.feed(chunk)  
        img = parser.close()
        list=[]
        uuid_str=str(uuid.uuid1())
        try:
            for std in args:
                w, h = std[0], std[1]  #获取照片的规格               
                filename=uuid_str+"-"+str(w)+"-"+str(h)+'.jpg'      
                opfile = os.path.join(self.check_folder(self.targetpath),filename)
                
                tempimg = self.pic_cut(img,int(w), int(h))
                tempimg.save(opfile, 'jpeg',quality=quality)
                list.append(filename)
            return list
        except:
            pass       
    
    def run_zoom_w(self,*args):
        '''运行图形缩放 接纳图形宽度tuple列表，每个宽度为一个整数'''
        parser = ImageFile.Parser()  
        for chunk in self.uploadedfile.chunks():  
            parser.feed(chunk)  
        img = parser.close()
        list=[]
        uuid_str=str(uuid.uuid1())
        w, h, isVertical = self.pic_info(img)
        try:
            for woh in args:#获取照片的宽度              
                th=int(float(woh) * self.comp_ratio(h,w))
                #生成唯一的图片名字     
                filename=uuid_str+"-"+str(woh)+"-"+str(th)+'.jpg'
                #图片路径+图片名字     
                opfile = os.path.join(self.check_folder(self.targetpath),filename)           
                tempimg=self.pic_zoom_w(img,int(woh))                
                tempimg.save(opfile, 'jpeg',quality=80)
                list.append(filename)
            return list
        except:
            pass
        
    def run_zoom_h(self,*args):
        '''运行图形缩放 接纳图形高度tuple列表，每个高度为一个整数'''
        parser = ImageFile.Parser()  
        for chunk in self.uploadedfile.chunks():  
            parser.feed(chunk)  
        img = parser.close()
        list=[]
        uuid_str=str(uuid.uuid1())
        w, h, isVertical = self.pic_info(img)
        try:
            for woh in args:#获取照片的高度                
                tw=int(float(woh) * self.comp_ratio(w,h))
                filename=uuid_str+"-"+str(tw)+"-"+str(woh)+'.jpg'   
                opfile = os.path.join(self.check_folder(self.targetpath),filename)                    
                tempimg=self.pic_zoom_h(img,int(woh))
                tempimg.save(opfile, 'jpeg',quality=80)
                list.append(filename)
            return list
        except:
            pass
        
    def run_thumbnail(self,*args):
        '''传统的生成缩略图 接纳规格列表，每个规格为一个tuple'''
        parser = ImageFile.Parser()  
        for chunk in self.uploadedfile.chunks():  
            parser.feed(chunk)  
        img = parser.close()
        list=[]
        uuid_str=str(uuid.uuid1())
        try:
            for std in args:
                #获取照片的规格            
                w, h = std[0], std[1]
                #生成唯一的图片名字         
                filename=uuid_str+"-"+str(w)+"-"+str(h)+'.jpg'
                #图片路径+图片名字
                opfile = os.path.join(self.check_folder(self.targetpath),filename)
                tempimg=img.copy()
                tempimg.thumbnail((int(w), int(h)),Image.ANTIALIAS)
                tempimg.save(opfile, 'jpeg',quality=80)
                list.append(filename)
            return list
        except:
            pass
    def run_thumb_all(self,*args):
        '''传统的生成缩略图 接纳规格列表，每个规格为一个tuple'''
        '''多个尺寸同时生成'''
        #parser = ImageFile.Parser()  
        #for chunk in self.uploadedfile.chunks():  
        #    parser.feed(chunk)  
        #img = parser.close()
        img = self.uploadedfile
        #list=[]
        #uuid_str=str(uuid.uuid1())
        for std in args:
            #获取照片的规格            
            w, h = std[0], std[1]
            #生成唯一的图片名字         
            filename= self.imagename
            #图片路径+图片名字
            opfile = os.path.join(self.check_folder(self.targetpath+str(w)+'/'),filename)
            tempimg=img.copy()
            tempimg.thumbnail((int(w), int(h)))
            #宽度大于200就加水印
            if w >200:
                WriteText(tempimg,'www.42ic.com',opfile)
            else:
                tempimg.save(opfile, 'jpeg',quality=80)
            #list.append(filename)
        return 'ok'

if __name__ == "__main__":
    im = Image.open( '/home/lyping/data/42ic/iadmin/utils/20111129102419ac973.jpg' ).convert("RGB")
    i = Graphics(im, '/home/lyping/data/42ic/iadmin/utils/','973.jpg');
    i.run_thumb_all([500,500],[100,100]);

var seting = {
    apiUrl: "/api",
    ratio: 0.618,
    types: 'all'
};
var jigsaw = {
    count: 0,
    halfHtml: '',
    loadBig: false,
    ajaxing: false
};

window.onresize = function () {
    resizeHeight()
};

window.onload = function () {
    loadCategories(); // 加载分类
    loadData(seting.types, true);
    resizeHeight()
};

$(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() + $(window).height() + 20 >= $(document).height() && $(this).scrollTop() > 20) {
            loadData(seting.types, false)
        }
    });
});


function loadCategories() {
    $.ajax({
            type: "GET",
            url: "/categories",
            dataType: "json",
        success: function (data) {
            if (data.code === 200 && data.categories) {
                var categories = data.categories;
                var categoriesList = $("#categories-list");
                categoriesList.empty();
                
                // 添加全部图片选项
                categoriesList.append('<li data-id="all" onclick="loadData(\'all\', true);changeTitle(this)" class="active">全部图片</li>');
                
                // 添加其他分类
                for (var i = 0; i < categories.length; i++) {
                    var category = categories[i];
                    categoriesList.append('<li data-id="' + category.id + '" onclick="loadData(\'' + category.id + '\', true);changeTitle(this)">' + category.name + '</li>');
                }
            }
        },
        error: function (xhr, status, error) {
            console.error("加载分类失败:", xhr, status, error);
            // 如果加载失败，显示默认分类
            var categoriesList = $("#categories-list");
            categoriesList.empty();
            categoriesList.append('<li data-id="all" onclick="loadData(\'all\', true);changeTitle(this)" class="active">全部图片</li>');
            categoriesList.append('<li data-id="test" onclick="loadData(\'test\', true);changeTitle(this)">测试分类</li>');
        }
    });
}

function loadData(types, newload) {
    if (types != seting.types || newload === true) {
        seting.types = types;
        jigsaw = {
            count: 0,
            halfHtml: '',
            loadBig: false,
            ajaxing: false
        };
        $("#walBox").html('');
        $(".onepage-pagination").remove();
        $("body").removeClass();
        $(".jigsaw").removeAttr("style")
        
        // 更新分类选中状态
        $("#categories-list li").removeClass("active");
        $("#categories-list li[data-id='" + types + "']").addClass("active");
    }
    ajax360Wal(seting.types, jigsaw.count, 30)
}

resizeHeight();

function resizeHeight() {
    switch (seting.types) {
        default:
            var newHeight = $("#walBox").width() * (seting.ratio / 2);
            $(".jigsaw .item").css('height', newHeight);
            $(".jigsaw .Hhalf").css('height', newHeight / 2)
    }
    return true
}

function addJigsaw(thumbnail, original, alt) {
    var newHtml;
    var imgWidth, imgHeight;
    jigsaw.count++;
    
    if (jigsaw.halfHtml !== '') {
        imgWidth = parseInt(screen.width / 4);
        imgHeight = parseInt(imgWidth * seting.ratio);
        newHtml = '<div class="Hhalf oneImg"><a href="' + original + '" data-fancybox="images"><img src="' + thumbnail + '" alt="' + alt + '" title="标签：' + alt + '" class="pimg"></a></div></div>';
        contAdd(jigsaw.halfHtml + newHtml);
        jigsaw.halfHtml = '';
        return true;
    }
    
    if (((jigsaw.count - 1) % 5) === 0) {
        jigsaw.loadBig = false;
    }
    
    if ((jigsaw.loadBig === false) && ((Math.floor(Math.random() * 3) === 0) || ((jigsaw.count % 5) === 0))) {
        imgWidth = parseInt(screen.width / 2);
        imgHeight = parseInt(imgWidth * seting.ratio);
        newHtml = '<div class="item half oneImg"><a href="' + original + '" data-fancybox="images"><img src="' + thumbnail + '" alt="' + alt + '" title="标签：' + alt + '" class="pimg"></a></div>';
        contAdd(newHtml);
        jigsaw.loadBig = true;
        return true;
    }
    
    imgWidth = parseInt(screen.width / 4);
    imgHeight = parseInt(imgWidth * seting.ratio);
    jigsaw.halfHtml = '<div class="item quater"><div class="Hhalf oneImg"><a href="' + original + '" data-fancybox="images"><img src="' + thumbnail + '" alt="' + alt + '" title="标签：' + alt + '" class="pimg"></a></div>';
    return true;
}

function contAdd(html) {
    var myBox = $("#walBox");
    var $newHtml = $(html);
    myBox.append($newHtml);
    $("img", $newHtml).lazyload({
        effect: 'fadeIn',
        threshold: 200
    })
}

function ajax360Wal(cid, start, count) {
    if (jigsaw.ajaxing === true) return false;
    $("#loadmore").html('努力加载中……');
    $("#loadmore").show();
    jigsaw.ajaxing = true;
    
    $.ajax({
        type: "GET",
        url: seting.apiUrl,
        data: "cid=" + cid + "&start=" + start + "&count=" + count,
        dataType: "json",
        success: function (jsonData) {
            console.log("API响应:", jsonData);
            
            // 检查响应格式
            if (jsonData.code === 200 && jsonData.data) {
                for (var i = 0; i < jsonData.data.length; i++) {
                    var imgData = jsonData.data[i];
                    console.log("处理图片:", imgData);
                    addJigsaw(imgData.thumbnail, imgData.url, imgData.tag || '未分类')
                }
                resizeHeight();
                jigsaw.ajaxing = false;
                
                if (jsonData.data.length === 0) {
                    $("#loadmore").html('所有的壁纸都已经加载完啦！')
                } else {
                    $("#loadmore").hide()
                }
            } else {
                console.error("API响应格式错误:", jsonData);
                $("#loadmore").html('加载失败，请刷新重试')
                jigsaw.ajaxing = false;
            }
        },
        error: function (xhr, status, error) {
            console.error("API请求失败:", xhr, status, error);
            $("#loadmore").html('网络错误，请检查服务器')
            jigsaw.ajaxing = false;
        }
    });
    return true
}

function changeTitle(obj) {
    $('title').html($(obj).html() + ' - 电脑壁纸')
}

// =======================================================
// 【修正】FancyBox v6.1 初始化
// =======================================================

// 确保 fancyBox 库已加载（由 CDN 引入）

// 绑定所有带有 data-fancybox="images" 属性的链接
document.addEventListener('DOMContentLoaded', function() {
    Fancybox.bind('[data-fancybox="images"]');
});




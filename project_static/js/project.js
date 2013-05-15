(function(window, $){
    $(function(){

        // login
        $('#accoutLogin').click(function(e){
            e.preventDefault();
            var email, passwd;
            email = $('#lEmail').val();
            passwd = $('#lP').val();

            email = strip(email);
            passwd = strip(passwd);



            if(email.length==0 || passwd.length==0) {
                make_warning('#loginWaring', '请填写电子邮件和密码');
                return false;
            }

            $.ajax(
                {
                    type: 'POST',
                    url: '/account/login/',
                    data: {
                        email: email,
                        passwd: passwd,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        if(data.ok) {
                            window.location.reload();
                        }
                        else {
                            make_warning('#loginWaring', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#loginWaring', '发生错误，请稍后再试')
                    }
                }
            );
        });



        // register 
        $('#accoutRegister').click(function(e){
            e.preventDefault();
            var email, username, passwd, passwd2;
            email = $('#rEmail').val();
            username = $('#rName').val();
            passwd = $('#rP').val();
            passwd2 = $('#rP2').val();

            email = strip(email);
            username = strip(username);
            passwd = strip(passwd);
            passwd2 = strip(passwd2);

            if(email.length == 0 || username.length == 0 || passwd.length == 0 || passwd2.length == 0) {
                make_warning('#registerWaring', '请完整填写注册信息');
                return false;
            }

            if(passwd != passwd2) {
                make_warning('#registerWaring', '两次密码不一致');
                return false;
            }


            $.ajax(
                {
                    type: 'POST',
                    url: '/account/register/',
                    data: {
                        email: email,
                        username: username,
                        passwd: passwd,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        if(data.ok) {
                            window.location.reload();
                        }
                        else {
                            make_warning('#registerWaring', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#registerWaring', '发生错误，请稍后再试')
                    }
                }
            );
        });









        //logout
        $('#accoutLogout').click(function(e){
            e.preventDefault();
            $.ajax(
                {
                    type: 'GET',
                    url: '/account/logout/',
                    async: false,
                    success: function(data){
                        window.location.reload();
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        window.location.reload();
                    }
                }
            );
        });



        // set mysign
        $('#mySignBtn').click(function(e){
            e.preventDefault();
            var mysign = $('#mySign').val();
            mysign = strip(mysign);


            if(mysign.length==0) {
                return false;
            }

            $.ajax(
                {
                    type: 'POST',
                    url: '/account/settings/mysign',
                    data: {
                        mysign: mysign,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        if(data.ok) {
                            make_warning('#mySignWarning', '设置成功');
                            $('#mySign').val('');
                        }
                        else {
                            make_warning('#loginWaring', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#loginWaring', '发生错误，请稍后再试')
                    }
                }
            );
        });




        // post new head 
        $('#postNewHead').click(function(e){
            e.preventDefault();
            var title, content;
            title = $('#nPostHead').val();
            content = $('#nPostContent').val();

            title = strip(title);
            content = strip(content);

            if(title.length == 0 || content.length == 0) {
                make_warning('#postHeadWarning', '填写标题和内容啊魂淡！');
                return false;
            }


            $.ajax(
                {
                    type: 'POST',
                    url: '/posts/head/new',
                    data: {
                        title: title,
                        content: content,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        if(data.ok) {
                            window.location = data.msg;
                        }
                        else {
                            make_warning('#postHeadWarning', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#postHeadWarning', '发生错误，请稍后再试')
                    }
                }
            );
        });




        // post new body 
        $('#postNewBody').click(function(e){
            e.preventDefault();
            var content = $('#nBodyContent').val();

            var head_id = undefined, parent_id = undefined;
            head_id = $('#nBodyHeadID').val();
            parent_id = $('#nBodyParentID').val();

            if(head_id === undefined || parent_id === undefined) {
                make_warning('#postBodyWarning', '有错误');
                return false;
            }

            content = strip(content);

            if(content.length == 0) {
                make_warning('#postBodyWarning', '填写内容啊魂淡！');
                return false;
            }


            $.ajax(
                {
                    type: 'POST',
                    url: '/posts/body/new',
                    data: {
                        head_id: head_id,
                        parent_id: parent_id,
                        content: content,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        if(data.ok) {
                            window.location = data.msg;
                        }
                        else {
                            make_warning('#postHeadWarning', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#postHeadWarning', '发生错误，请稍后再试')
                    }
                }
            );
        });


        $('.can-score-good').click(function(){
            var pid = $(this).attr('id').split('-')[1];
            $.ajax(
                {
                    type: 'POST',
                    url: '/score/post/good/' + pid,
                    data: {
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: true,
                    success: function(data){
                        console.log(data);
                        if(data === 1) {
                            var $thisitem = $('#scoregood-' + pid);
                            $thisitem.find('.icon').css('background-position', $thisitem.attr('hover_bg_pos'));
                            var oldnum = $thisitem.find('.num').text();
                            $thisitem.find('.num').text(parseInt(oldnum) + 1);
                            return;
                        }
                        else {
                            return;
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        return;
                    }
                }
            );
        });



        $('.can-score-bad').click(function(){
            var pid = $(this).attr('id').split('-')[1];
            $.ajax(
                {
                    type: 'POST',
                    url: '/score/post/bad/' + pid,
                    data: {
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: true,
                    success: function(data){
                        console.log(data);
                        if(data === 1) {
                            var $thisitem = $('#scorebad-' + pid);
                            $thisitem.find('.icon').css('background-position', $thisitem.attr('hover_bg_pos'));
                            var oldnum = $thisitem.find('.num').text();
                            $thisitem.find('.num').text(parseInt(oldnum) + 1);
                            return;
                        }
                        else {
                            return;
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        return;
                    }
                }
            );
        });





        // change background position
        /*
        $('.item-button').mouseenter(function(){
            var $icon = $(this).find('.icon');
            var unhover_pos = $icon.css('background-position');
            $(this).attr('unhover_bg_pos', unhover_pos);
            $icon.css('background-position', $(this).attr('hover_bg_pos'));
        }).mouseleave(
            function(){
                $(this).find('.icon').css('background-position', $(this).attr('unhover_bg_pos'));
            }
                               
        );
       */




        // list-view-action
        $('.list-view .content').mouseenter(function(){
            $(this).find('.list-view-action').show();
        }).mouseleave(function(){
            $(this).find('.list-view-action').hide();
        })



        // toggle forks area
        $('.has-fork').click(function(){
            var fid, show;
            fid = $(this).attr('fork-id');
            show = $('#forksarea' + fid).attr('show');
            if(show === '0') {
                $('#forksarea' + fid).attr('show', '1').slideDown(200);
                $(this).find('.text').text('收起分支');
            }
            else {
                $('#forksarea' + fid).attr('show', '0').slideUp(200);
                $(this).find('.text').text('打开分支');
            }
        });


        // fork-line-var height
        $('.list-view').each(function(index, obj){
            $(obj).find('.item-line').css('height', $(obj).height() + 20);
        })





    });


    function strip(value){
        return value.replace(/(^\s+|\s+$)/, '');
    }

    function get_csrf(){
        return $('input[name=csrfmiddlewaretoken]').attr('value');
    }

    function make_warning(obj, text) {
        $(obj).text(text);
        $(obj).show(100);
    }




})(window, jQuery);


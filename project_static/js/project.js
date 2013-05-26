(function(window, $){
    $(function(){
        $('a.dropdown').click(function(e){
            e.preventDefault();
        });



        // login
        $('#accoutLogin').click(function(e){
            e.preventDefault();
            var email, passwd;
            email = $('#lEmail').val();
            passwd = $('#lP').val();

            email = strip(email);
            passwd = strip(passwd);



            if(email.length===0 || passwd.length===0) {
                make_warning('#loginWarning', '请填写电子邮件和密码');
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
                            make_warning('#loginWarning', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#loginWarning', '发生错误，请稍后再试');
                    }
                }
            );
        });



        // register 
        $('#accoutRegister').click(function(e){
            e.preventDefault();
            var email, username, passwd, passwd2, _tmp_email;
            email = $('#rEmail').val();
            username = $('#rName').val();
            passwd = $('#rP').val();
            passwd2 = $('#rP2').val();

            email = strip(email);
            username = strip(username);
            passwd = strip(passwd);
            passwd2 = strip(passwd2);

            _tmp_email = email.replace(/^.+@.+\..+$/, '');
            if(_tmp_email.length>0){
                make_warning('#registerWarning', '喂，目测邮箱格式不正确啊');
                return false;
            }

            if(email.length === 0 || username.length === 0 || passwd.length === 0 || passwd2.length === 0) {
                make_warning('#registerWarning', '请完整填写注册信息');
                return false;
            }

            if(passwd != passwd2) {
                make_warning('#registerWarning', '两次密码不一致');
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
                            make_warning('#registerWarning', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#registerWarning', '发生错误，请稍后再试');
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
                            make_warning('#loginWarning', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#loginWarning', '发生错误，请稍后再试');
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

            if(title.length === 0 || content.length === 0) {
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
                        make_warning('#postHeadWarning', '发生错误，请稍后再试');
                    }
                }
            );
        });




        // post new body 
        $('#postNewBody').click(function(e){
            e.preventDefault();
            var content = $('#nBodyContent').val();

            var head_id, parent_id, item_last;
            head_id = $('#nBodyHeadID').val();
            parent_id = $('#nBodyParentID').val();
            item_last = $('#item' + parent_id).attr('item-last');

            if(head_id === undefined || parent_id === undefined) {
                make_warning('#postBodyWarning', '有错误');
                return false;
            }

            content = strip(content);

            if(content.length === 0) {
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
                        item_last: item_last,
                        content: content,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        if(data.ok) {
                            $('#postbody-modal').bPopup().close();
                            $('#nBodyContent').val('');
                            if(data.last){
                                $('#item' + parent_id).after(data.msg);
                                var $item_line = $('<div class="item-line" />');
                                $item_line.css('height', $('#item' + parent_id).height());
                                $('#item' + parent_id).append($item_line);
                                $('#item' + parent_id).attr('item-last', 0);
                                $('#item' + data.itemid).attr('item-last', 1);
                            }
                            else{
                                $('#forksarea' + parent_id).append(data.msg);
                                var new_height = $('#item' + parent_id).height();
                                $('#item' + parent_id).find('.item-line').addClass('fork').height(new_height);

                                var index, forkingitemsLength = forkingitems.length;
                                for(index=0; index<forkingitemsLength; index++) {
                                    if(forkingitems[index].fid === parent_id) {
                                        forkingitems[index].max_height = new_height;
                                        break;
                                    }
                                }
                            }
                            toggle_list_view_action();
                            open_body_modal();
                            $('html').scrollTo('#item' + data.itemid, 200);
                        }
                        else {
                            make_warning('#postBodyWarning', data.msg);
                        }
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        make_warning('#postBodyWarning', '发生错误，请稍后再试');
                    }
                }
            );
        });


        /*
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
*/


        // input character limit
        $('#nPostHead').charcount({
            maxLength: 40,
            position: 'none'
        }).bind('update', function(evt, length, remaining){
            $(this).next().find('span').text(remaining);
        });

        $('#nPostContent').charcount({
            maxLength: 255,
            position: 'none'
        }).bind('update', function(evt, length, remaining){
            $(this).next().find('span').text(remaining);
        });

        $('#nBodyContent').charcount({
            maxLength: 255,
            position: 'none'
        }).bind('update', function(evt, length, remaining){
            $(this).next().find('span').text(remaining);
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
        toggle_list_view_action();



        // toggle forks area
        /*
        $('.has-fork').click(function(){
            var fid, show, $pa, $item_line;
            fid = $(this).attr('fork-id');
            show = $('#forksarea' + fid).attr('show');
            $pa = $(this).parent().parent().parent().parent();
            $item_line = $pa.find('.item-line');
            console.log($pa.height());

            if(show === '0') {
                $('#forksarea' + fid).attr('show', '1').slideDown(200);
                $(this).find('.text').text('收起分支');
            }
            else {
                $('#forksarea' + fid).attr('show', '0').slideUp(200);
                $(this).find('.text').text('打开分支');
            }
            $item_line.css('height', $('.has-fork').parent().parent().parent().parent().height());
        });
       */
        var forkingitems = [];
        $('.has-fork').each(function(index, obj){
            forkingitems.push(
                new ForkingListItem( $(this), $(this).attr('fork-id') )
            );

            $(this).unbind('click');
            $(this).bind('click', function(){
                forkingitems[index].toggle();
            });
        });


        // fork-line-var height
        $('.list-view').each(function(index, obj){
            $(obj).find('.item-line').css('height', $(obj).height() + 20);
        });


        /*
        $('.content').mouseover(function(){
            $(this).parent().find('.avatar img').first().addClass('bigger');
        }).mouseout(function(){
            $(this).parent().find('.avatar img').first().removeClass('bigger');
        });
*/

        $('.index-item').mouseover(function(){
            $(this).find('.avatar img').first().addClass('bigger');
        }).mouseout(function(){
            $(this).find('.avatar img').first().removeClass('bigger');
        });


        // background highlight for cursor hover
        $('.index-item').mouseover(function(){
            $(this).addClass('item-bg-yellowLight');
        }).mouseout(function(){
            $(this).removeClass('item-bg-yellowLight');
        });


        get_notifies();

    });


    function strip(value){
        return value.replace(/(^\s+|\s+$)/, '');
    }

    function get_csrf(){
        return $('input[name=csrfmiddlewaretoken]').attr('value');
    }


    function toggle_list_view_action() {
        $('.list-view .content').bind('mouseenter', function(){
            // $(this).unbind('mouseenter');
            $(this).find('.list-view-action').show();
            $(this).addClass('item-bg-yellowLight');
            $(this).parent().find('.avatar img').first().addClass('bigger');
        }).bind('mouseleave', function(){
            // $(this).unbind('mouseleave');
            $(this).find('.list-view-action').hide();
            $(this).removeClass('item-bg-yellowLight');
            $(this).parent().find('.avatar img').first().removeClass('bigger');
        });
    }

    // $('.list-view .content').mouseenter(function(){
    //     $(this).find('.list-view-action').show();
    // }).mouseleave(function(){
    //     $(this).find('.list-view-action').hide();
    // });



    function make_warning(obj, text) {
        $(obj).text(text);
        $(obj).show(100);
    }


    var ForkingListItem = (function(){
        function ForkingListItem(obj, fid) {
            this.obj = obj;
            this.fid = fid;
            this.pa = this.obj.parent().parent().parent().parent();
            this.max_height = this.pa.height() + 20;
            this.min_height = this.pa.find('.content').first().height() + 40;
            this.item_line = this.pa.find('.item-line');
        }


        ForkingListItem.prototype.upit = function() {
            $('#forksarea' + this.fid).attr('show', '0').slideUp(200);
            this.obj.find('.text').text('打开分支');
            this.item_line.css('height', this.min_height);
        };

        ForkingListItem.prototype.downit = function() {
            $('#forksarea' + this.fid).attr('show', '1').slideDown(200);
            this.obj.find('.text').text('收起分支');
            this.item_line.css('height', this.max_height);
        };

        ForkingListItem.prototype.toggle = function() {
            var show = $('#forksarea' + this.fid).attr('show');
            if(show === '1') {
                this.upit();
            }
            else {
                this.downit();
            }
        };

        return ForkingListItem;
    })();






    // get notifies
    function get_notifies() {
        $.ajax(
            {
                type: 'GET',
                url: '/notifies',
                data: {},
                dateType: 'json',
                async: true,
                success: function(data){
                    if(data.length>0) {
                        var len = data.length >= 100 ? '99+' : data.length;
                        $('#notifya span').text(len);
                        var $ul = $('#notifya').next();
                        data.forEach(function(item){
                            var $li = $('<li class="link" />');
                            $li.append(item);
                            $li.appendTo($ul);
                        });
                        bind_noify_click_event();
                    }
                    else {
                    }
                },
                error: function(XmlHttprequest, textStatus, errorThrown){
                }
            }
        );
    }


    function bind_noify_click_event() {
        $('a.notifyme').click(function(){
            var nid = $(this).attr('noti-id');
            $.ajax(
                {
                    type: 'POST',
                    url: '/notify/confirm',
                    data: {
                        nid: nid,
                        csrfmiddlewaretoken: get_csrf()
                    },
                    dateType: 'json',
                    async: false,
                    success: function(data){
                        return true;
                    },
                    error: function(XmlHttprequest, textStatus, errorThrown){
                        return true;
                    }
                }
            );
        });
    }






})(window, jQuery);


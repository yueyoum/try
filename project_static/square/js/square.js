(function(window, $){
    $(function(){
        var dropdowns = [];
        $('#nav-bar .dropdown').each(function(index, obj){
            dropdowns.push(
                new NavDorpDown($(obj).next())
            );

            var left_offset_additon = $(this).attr('left-offset-addition');
            left_offset_additon = left_offset_additon == undefined ? 0 : parseInt(left_offset_additon);

            $(this).unbind('mouseenter').unbind('mouseleave');
            $(this).bind('mouseenter', function(){
                if($(this).attr('dropdown_align') === 'right')
                    dropdowns[index].show_right(
                        $('#nav-bar').height(),
                        $(document).width() - $(obj).offset().left - $(obj).width() - 20 - left_offset_additon);
                else
                    dropdowns[index].show($('#nav-bar').height(), $(obj).offset().left - left_offset_additon);
            }).bind('mouseleave', function(){
                dropdowns[index].hidden();
            })
        });


        $('.open-modal').bind('click', function(e){
            e.preventDefault();
            var wid = $(this).attr('modal-window-id');
            console.log(wid);
            open_modal_window(wid);
        });

        open_body_modal();




        $('#postbody-modal').find('.close').bind('click', function(){
            //$(this).unbind('click');
            $('#nBodyContent').val('');
            $('#postBodyWarning').text('');
            $('#postbody-modal').bPopup().close();
        });

        $('#posthead-modal').find('.close').bind('click', function(){
            $('#nPostHead').val('');
            $('#nPostContent').val('');
            $('#postHeadWarning').text('');
            $('#posthead-modal').bPopup().close();
        })


    });



    var NavDorpDown = (function(){
        // dorpdown menu
        function NavDorpDown(obj) {
            this.obj = obj;
            this.timer = null;

            var self = this;
            this.obj.unbind('mouseenter').unbind('mouseleave');
            this.obj.bind('mouseenter', function(){
                if(self.timer) {
                    window.clearTimeout(self.timer);
                    self.timer = null;
                }
            }).bind('mouseleave', function(){
                self.real_hidden();
                self.timer = null;
            });
        }

        NavDorpDown.prototype.timeout = 500;

        NavDorpDown.prototype.show = function(top, left) {
            this.obj.css('top', top
                    ).css('left', left
                    ).css('display', 'block');
        }

        NavDorpDown.prototype.show_right = function(top, right) {
            this.obj.css('top', top
                    ).css('right', right 
                    ).css('display', 'block');
        }


        NavDorpDown.prototype.hidden = function() {
            var self = this;
            self.timer = window.setTimeout(function(){self.real_hidden();}, self.timeout);
        }

        NavDorpDown.prototype.real_hidden = function() {
            this.obj.css('display', 'none');
        }

        return NavDorpDown;
    })();





})(window, jQuery);

    // open modal window
    var open_modal_window = (function(){
        var pstyle = navigator.appName === 'Microsoft Internet Explorer' ? 'absolute' : 'fixed';

        var _open = function(wid) {
            // if($('#'+wid).attr('auto-close') === '1') {
            //     $('#' + wid).children('.header').children('.close').bind('click', function(){
            //         $(this).unbind('click');
            //         $('#' + wid).bPopup().close();
            //     });
            // }
            $('#' + wid).bPopup({
                followSpeed: 100,
                opacity: 0.4,
                positionStyle: pstyle,
                transition: 'slideDown'
            });
        };

        return _open;
    })();


    function open_body_modal() {
        $('.open-body-modal').bind('click', function(e){
            e.preventDefault();
            var wid = $(this).attr('modal-window-id');

            var text = $(this).parent().parent().parent().find('p.text').text();
            $('#' + wid).find('div.oldtext').text(text);
            open_modal_window(wid);

            var head_id, parent_id;
            head_id = $(this).attr('head-id');
            parent_id = $(this).attr('parent-id');
            if(head_id !== undefined && parent_id !== undefined) {
                $('#nBodyHeadID').val(head_id);
                $('#nBodyParentID').val(parent_id);
            }
        });
    }


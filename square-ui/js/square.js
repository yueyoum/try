(function(window, $){
    $(function(){
        var nav_height = $('#nav-bar').height();
        var dropdowns = [];
        $('#nav-bar a.dropdown').each(function(index, obj){
            dropdowns.push(
                new NavDorpDown($(obj).next())
            );

            var left_offset_additon = $(this).attr('left-offset-addition');
            left_offset_additon = left_offset_additon == undefined ? 0 : parseInt(left_offset_additon);

            $(this).unbind('mouseover').unbind('mouseout');
            $(this).bind('mouseover', function(){
                dropdowns[index].show(nav_height, $(obj).offset().left + left_offset_additon);
            }).bind('mouseout', function(){
                dropdowns[index].hidden();
            })
        });
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

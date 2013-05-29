function inittree(data, start_id) {
    var st = new $jit.ST({
        orientation: 'top',
        injectInto: 'treeNavs',
        duration: 300,
        transition: $jit.Trans.Quart.easeInOut,
        levelDistance: 40,
        levelsToShow: 4,
        Navigation: {
          enable:true,
          panning:true
        },
        Node: {
            height: 20,
            width: 40,
            dim: 30,
            type: 'circle',
            color: '#aaa',
            overridable: true
        },

        Edge: {
            type: 'bezier',
            overridable: true
        },

        onBeforeCompute: function(node){
            // Log.write("loading " + node.name);
        },

        onAfterCompute: function(){
            // Log.write("done");
        },

        onCreateLabel: function(label, node){
            label.id = node.id;
            label.innerHTML = '#' + (node._depth + 1) + node.data.b;
            label.onclick = function(){
              st.onClick(node.id);
              var $thisItem = $('#item' + node.id);
              if($thisItem.length){
                $('html').scrollTo('#item' + node.id, 200);
              }
              else{
                window.location.href = '/posts/' + node.id;
              }
            };
            var style = label.style;
            style.width = 40 + 'px';
            style.height = 20 + 'px';
            style.cursor = 'pointer';
            style.color = '#fff';
            style.fontSize = '12px';
            style.textAlign= 'center';
            style.paddingTop = '3px';
        },

        //This method is called right before plotting
        //a node. It's useful for changing an individual node
        //style properties before plotting it.
        //The data properties prefixed with a dollar
        //sign will override the global node style properties.
        onBeforePlotNode: function(node){
            //add some color to the nodes in the path between the
            //root node and the selected node.
            if (node.selected) {
                node.data.$color = "#01938E";
            }
            else {
                delete node.data.$color;
                //if the node belongs to the last plotted level
                /*
                if(!node.anySubnode("exist")) {
                    //count children number
                    var count = 0;
                    node.eachSubnode(function(n) { count++; });
                    //assign a node color based on
                    //how many children it has
                    node.data.$color = ['#aaa', '#baa', '#caa', '#daa', '#eaa', '#faa'][count];                    
                }
                */
            }
        },

        //This method is called right before plotting
        //an edge. It's useful for changing an individual edge
        //style properties before plotting it.
        //Edge data proprties prefixed with a dollar sign will
        //override the Edge global style properties.
        onBeforePlotLine: function(adj){
            if (adj.nodeFrom.selected && adj.nodeTo.selected) {
                adj.data.$color = "#08ACA6";
                adj.data.$lineWidth = 3;
            }
            else {
                delete adj.data.$color;
                delete adj.data.$lineWidth;
            }
        }
    });
    //load json data
    st.loadJSON(data);
    //compute node positions and layout
    st.compute();
    //optional: make a translation of the tree
    st.geom.translate(new $jit.Complex(-200, 0), "current");
    //emulate a click on the root node.
    st.onClick(start_id);
    //end
    //Add event handlers to switch spacetree orientation.
    return st;
}


$(function(){
    var head_id = $('#headID').text();
    var start_id = $('#startID').text();
    var st;
    if(head_id!=="" && start_id!==""){
          $.ajax(
            {
              type: 'GET',
              url: '/posts/treestruct/' + head_id,
              data: {},
              dataType: 'json',
              async: false,
              success: function(data){
                st = inittree(data, start_id);
              },
              error: function(a, b, c) {
                console.log('get data error...');
              }
            }
          );
    }

    $('.list-view .content').mouseenter(function(){
        var pid = $(this).attr('id').split('content')[1];
        st.onClick(pid);
    });
});

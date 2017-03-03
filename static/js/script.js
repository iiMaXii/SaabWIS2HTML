$( document ).ready(function() {
  var submenus = {};
/*
		$("#tabmenu").tabs("disable");
		$.each(submenus[id], function(key, value) {
			console.log(value);

			$('div#'+key).jstree({
				'core' : {
					'themes':{
						'icons':false
					},
					'multiple' : false,
					'data' : value
				}
			});


			$("#tabmenu").tabs("enable", '#'+key);

			$('div#'+key).on("dblclick.jstree", function (event) {
				var node = $(event.target).closest("li");
				var data = node.data("jstree");
				console.log('loading page');
				//$('#'+key).load('data/'+LANGUAGE+'/doc'+node.attr('id')+'.htm');
				$('#content_frame').attr('src','data/'+LANGUAGE+'/doc'+node.attr('id')+'.htm');
				console.log('page loaded');
			});

		});
*/

  console.log('Loading menu.json');
  $.getJSON("/static/data/se/index/menu.json", function(data) {
    console.log('Got menu.json');
    $('#treeview1').treeview({
      data: data,
      onNodeSelected: function(event, data) {
        var active_tab_id = data['data-id'];
        console.log(data['data-id']);
        if (jQuery.isEmptyObject(submenus)) {
          alert('Still loading, please wait');
          return;
        }

        $('#tab-menu li').each(function(index) {
          $(this).addClass('disabled');
        });

        // Clear content of all tabs
        $('div[role=tab-content]').empty();
        $('div[role=tab-content]').removeClass('active');

        $.each(submenus[active_tab_id], function(id, value) {
		  $('#tab-tree-'+id).treeview({
		    data: value,
		    onNodeSelected: function(event, data) {
		      console.log('Loading doc'+data['data-id']+' into tab'+id)
		      console.log("/static/data/se/doc"+data['data-id']+".html");
		      $('#tab-content-'+id).load("/static/data/se/doc"+data['data-id']+".html", function() {
		        console.log("Enabling img modal");
		        var modal = document.getElementById('myModal');
		        var modalImg = document.getElementById("img01");
		        $('#tab-content-'+id+' img').click(function() {
 		          //var captionText = document.getElementById("caption");
 		          modal.style.display = "block";
		          modalImg.src = this.src;
		          $("#myModal").modal();
		        });
		      });

		    }
		  });
		  console.log('Activating tab id='+id)
		  $('#tab-'+id).removeClass('disabled');

        });
      }
    });
  });

  console.log('Loading tabs.json');
  $.getJSON("/static/data/se/index/tabs.json", function(data) {
    console.log('Got tabs.json');
    $.each(data, function (index, data) {
        $('#tab-menu').append('<li id="tab-'+data.id+'" class="nav-item disabled"><a class="nav-link" data-toggle="tab" href="#tab-pane-'+data.id+'" role="tab">'+data.name+'</a></li>');
        $('#tab-content').append('<div class="tab-pane active" id="tab-pane-'+data.id+'" role="tabpanel"><div id="tab-content-'+data.id+'" role="tab-content"></div><div id="tab-tree-'+data.id+'"></div></div>');
    })
  });

  console.log('Loading submenus.json');
  $.getJSON("/static/data/se/index/submenus.json", function(data) {
    console.log('Got submenus.json');
    submenus = data;
  });

  //

  /*$('#myModal').click(function() {
    document.getElementById('myModal').style.display='none'
  });*/

  $('#img01').click(function() {
    window.location = this.src;
  });

// Get the modal


// Get the <span> element that closes the modal
//var span = document.getElementsByClassName("close")[0];

// When the user clicks on <span> (x), close the modal
/*$('#myModal .close')
span.onclick = function() {
  modal.style.display = "none";
}*/

});

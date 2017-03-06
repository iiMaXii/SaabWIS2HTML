var submenus = {};
var active_tab = -1;

$(document).ready(function() {
  console.log('Loading tabs.json');
  $.getJSON("/static/data/se/index/tabs.json", function(data) {
    console.log('Got tabs.json');
    $.each(data, function (index, data) {
        $('#tab-menu').append('<li id="tab-'+data.id+'" class="nav-item disabled"><a class="nav-link" data-toggle="tab" href="#tab-pane-'+data.id+'" role="tab">'+data.name+'</a></li>');
        $('#tab-content').append('<div class="tab-pane active" id="tab-pane-'+data.id+'" role="tabpanel"><div id="tab-content-'+data.id+'" role="tab-content"></div><div id="tab-tree-'+data.id+'" role="tab-submenu-tree"></div></div>');
    })
  });

  $.getJSON("/static/data/se/index/menu.json", function(data) {
    $('#treeview1').treeview({
      data: data,
      onNodeSelected: function(event, data) {
        var submenu_identifier = data['data-id'];
        console.log('Loading submenu '+submenu_identifier);
        if (jQuery.isEmptyObject(submenus)) {
          alert('Still loading, please wait');
          return;
        }

        $('#tab-menu li').addClass('disabled');

        // Clear content of all tabs
        $('div[role=tab-content]').empty();
        //$('div[role=tab-submenu-tree]').treeview('remove');
        $('.treeview[role=tab-submenu-tree]').each(function(index) {
          if ($(this).hasClass('treeview')) {
            $(this).treeview('remove');
          }
        });
        $('div[role=tabpanel]').removeClass('active');

        $.each(submenus[submenu_identifier], function(id, value) {
		  $('#tab-tree-'+id).treeview({
		    data: value,
		    onNodeSelected: function(event, data) {
		      active_tab = id;
		      console.log('Loading doc'+data['data-id']+' into tab'+id)
		      console.log("/static/data/se/doc"+data['data-id']+".html");
		      $('#tab-content-'+id).load("/static/data/se/doc"+data['data-id']+".html", function() {
		        var modal = document.getElementById('myModal');
		        var modalImg = document.getElementById("img01");
		        $('#tab-content-'+id+' img').click(function() {
 		          //var captionText = document.getElementById("caption");
 		          modal.style.display = "block";
		          modalImg.src = this.src;
		          $("#myModal").modal();
		        }).css('cursor', 'pointer');
		      });

		    }
		  });
		  console.log('Activating tab id='+id)
		  $('#tab-'+id).removeClass('disabled');

        });
      }
    });
  });

  console.log('Loading submenus.json');
  $.getJSON("/static/data/se/index/submenus.json", function(data) {
    console.log('Got submenus.json');
    submenus = data;
  });

  $('#img01').click(function() {
    window.location = this.src;
  });



});

function open_doc(document_identifier) {
  if (active_tab == -1) {
    alert('Error: No tab active');
    return;
  }
  console.log('Loading doc'+document_identifier+' into tab'+active_tab)
  $('#tab-content-'+active_tab).load("/static/data/se/doc"+document_identifier+".html", function() {
    var modal = document.getElementById('myModal');
    var modalImg = document.getElementById("img01");
    $('#tab-content-'+active_tab+' img').click(function() {
      //var captionText = document.getElementById("caption");
      modal.style.display = "block";
      modalImg.src = this.src;
      $("#myModal").modal();
    }).css('cursor', 'pointer');
  });
}
